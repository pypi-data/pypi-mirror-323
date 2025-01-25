import os
import pprint
import tempfile as tmp
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Mapping, Optional, Union

import orjson
import polars as pl
from fastapi import HTTPException
from fastapi.responses import FileResponse, PlainTextResponse, Response
from starlette.background import BackgroundTask

from tesseract_olap.backend import Result
from tesseract_olap.common import AnyDict
from tesseract_olap.query import DataQuery, DataRequest, MembersQuery, MembersRequest
from tesseract_olap.schema import Annotations, MemberType, TesseractProperty


class ResponseFormat(Enum):
    csv = "csv"
    excel = "xlsx"
    jsonarrays = "jsonarrays"
    jsonrecords = "jsonrecords"
    parquet = "parquet"
    tsv = "tsv"


MIMETYPES = {
    ResponseFormat.csv: "text/csv",
    ResponseFormat.excel: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ResponseFormat.jsonarrays: "application/json",
    ResponseFormat.jsonrecords: "application/json",
    ResponseFormat.parquet: "application/vnd.apache.parquet",
    ResponseFormat.tsv: "text/tab-separated-values",
}


@dataclass(eq=False, order=False)
class MembersResModel:
    name: str
    caption: str
    depth: int
    annotations: Annotations
    properties: List["TesseractProperty"]
    dtypes: Mapping[str, MemberType]
    members: List[AnyDict]


def data_response(
    result: Result[pl.DataFrame],
    extension: ResponseFormat,
    *,
    annotations: Union[Annotations, AnyDict],
    tempdir: Union[str, Path],
) -> Response:
    df = result.data
    columns = tuple(df.columns)

    headers = {
        "X-Tesseract-Cache": result.cache.get("status", "MISS"),
        "X-Tesseract-Columns": ",".join(columns),
        "X-Tesseract-QueryRows": str(df.height),
        "X-Tesseract-TotalRows": str(result.page["total"]),
    }
    kwargs: AnyDict = {"headers": headers, "media_type": MIMETYPES[extension]}

    if extension is ResponseFormat.csv:
        content = df.write_csv(separator=",", include_header=True)
        return PlainTextResponse(content, **kwargs)

    elif extension is ResponseFormat.tsv:
        content = df.write_csv(separator="\t", include_header=True)
        return PlainTextResponse(content, **kwargs)

    elif extension is ResponseFormat.jsonarrays:
        res = df.to_dict(as_series=False)
        target = {
            "annotations": dict(annotations),
            "columns": columns,
            "data": list(zip(*(res[key] for key in columns))),
            "page": result.page,
        }
        content = orjson.dumps(target)
        return PlainTextResponse(content, **kwargs)

    elif extension is ResponseFormat.jsonrecords:
        target = {
            "annotations": dict(annotations),
            "columns": columns,
            "data": df.to_dicts(),
            "page": result.page,
        }
        content = orjson.dumps(target)
        return PlainTextResponse(content, **kwargs)

    elif extension is ResponseFormat.excel:
        with tmp.NamedTemporaryFile(
            delete=False, dir=tempdir, suffix=f".{extension}"
        ) as tmp_file:
            df.write_excel(tmp_file.name)

        kwargs["filename"] = f"data_{result.cache['key'][0:8]}.{extension}"
        kwargs["background"] = BackgroundTask(os.unlink, tmp_file.name)
        return FileResponse(tmp_file.name, **kwargs)

    elif extension is ResponseFormat.parquet:
        with tmp.NamedTemporaryFile(
            delete=False, dir=tempdir, suffix=f".{extension}"
        ) as tmp_file:
            df.write_parquet(tmp_file.name)

        kwargs["filename"] = f"data_{result.cache['key'][0:8]}.{extension}"
        kwargs["background"] = BackgroundTask(os.unlink, tmp_file.name)
        return FileResponse(tmp_file.name, **kwargs)

    raise HTTPException(406, f"Requested format is not supported: {extension}")


def members_response(
    params: MembersRequest,
    query: MembersQuery,
    result: Result[List[AnyDict]],
):
    locale = query.locale
    level = query.hiefield.deepest_level.level
    with_parents = params.options["parents"]

    return MembersResModel(
        name=level.name,
        caption=level.get_caption(locale),
        depth=level.depth,
        annotations=dict(level.annotations),
        properties=[
            TesseractProperty.from_entity(item, locale) for item in level.properties
        ],
        dtypes=result.columns,
        members=[nest_keys(row) for row in result.data]
        if with_parents
        else result.data,
    )


def nest_keys(item: dict):
    return build_member(
        key=item.pop("key"),
        caption=item.pop("caption", None),
        ancestor=tuple(gen_ancestor_members(item, "ancestor")),
    )


def gen_ancestor_members(item: dict, prefix: str):
    index = 0
    while True:
        if f"{prefix}.{index}.key" not in item:
            break
        yield build_member(
            key=item.pop(f"{prefix}.{index}.key"),
            caption=item.pop(f"{prefix}.{index}.caption", None),
        )
        index += 1


def build_member(*, caption: Optional[str] = None, **kwargs):
    if caption is not None:
        kwargs["caption"] = caption
    return kwargs


def debug_response(
    accept: str, *, request: DataRequest, query: DataQuery, sql: AnyDict
) -> Response:
    priority = [item.split(";")[0] for item in accept.split(",")]
    restype = sorted(
        ["text/plain", "application/json", "text/html"],
        key=lambda x: priority.index(x) if x in priority else 99,
    )

    def _dict_2_str(obj: dict, *, title: str = "{}", content: str = "{}"):
        return "\n".join(
            title.format(name) + "\n" + content.format(value)
            for name, value in obj.items()
            if value
        )

    if restype[0] == "text/plain":
        queries = {
            f"Fetch {name.capitalize()}": _dict_2_str(
                {
                    "SQL": value["query"],
                    "Params": pprint.saferepr(value["params"])
                    if value["params"]
                    else None,
                    "Tables": _dict_2_str(
                        {
                            f"Table {table_name!r}": "\n".join(
                                "\t".join(str(cell) for cell in row)
                                for row in table_body
                            )
                            for table_name, table_body in value["tables"].items()
                        },
                        title="### {}",
                    ),
                },
                title="## {}",
            )
            for name, value in sql.items()
        }
        sections = {
            "DataRequest": pprint.pformat(request, sort_dicts=True),
            "DataQuery": pprint.saferepr(query),
            **queries,
        }
        content = _dict_2_str(sections, title="\n# {}")
        return PlainTextResponse(content, media_type="text/plain")

    if restype[0] == "text/html":
        queries = {
            f"Fetch {name.capitalize()}": _dict_2_str(
                {
                    "SQL": f"<pre>{value['query']}</pre>",
                    "Params": f"<pre>{pprint.saferepr(value['params'])}</pre>",
                    "Tables": _dict_2_str(
                        {
                            f"Table {table_name!r}": "".join(
                                f'<tr>{"".join(f"<td>{cell}</td>" for cell in row)}</tr>'
                                for row in table_body
                            )
                            for table_name, table_body in value["tables"].items()
                        },
                        title="<h4>{}</h4>",
                        content="<table><tbody>{}</tbody></table>",
                    ),
                },
                title="<h3>{}</h3>",
            )
            for name, value in sql.items()
        }
        sections = {
            "DataRequest": f"<pre>{pprint.pformat(request, sort_dicts=True)}</pre>",
            "DataQuery": f"<pre>{pprint.saferepr(query)}</pre>",
            **queries,
        }
        content = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8" /><style>pre{{white-space:normal}}</style></head>
<body>{_dict_2_str(sections, title="<h2>{}</h2>")}</body>
</html>
"""
        return PlainTextResponse(content, media_type="text/html")

    content = {
        "request": pprint.pformat(request, sort_dicts=True),
        "query": pprint.saferepr(query),
        **sql,
    }
    return PlainTextResponse(orjson.dumps(content), media_type="application/json")
