from typing import Union, List, Dict
import os
import json
from urllib.parse import urlparse, parse_qs
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from . import _constants as constants
from ._utils import request, parse_to_str
from ._utils import RequestMode, RequestContent


class Connector:
    def __init__(
        self,
        domain: str,
        token: str,
        verify_ssl: bool = False,
    ):
        self._token = token
        self._verify_ssl = verify_ssl

        link = urlparse(domain)
        if len(link.netloc) == 0:
            raise ValueError(f"invalid domain: {domain}")

        params = dict(parse_qs(link.query))
        params = {k: v[0] for k, v in params.items()}
        self.params = params
        self._domain = f"{link.scheme}://{link.netloc}{link.path}"

    def request(
            self,
            url: str,
            req: RequestContent,
            mode: str = RequestMode.POST,
    ):
        for k, v in self.params.items():
            req.params[k] = v
        req.headers = {constants.TOKEN_KEY: self._token}

        res = request(
            url=url.replace(os.sep, "/"),
            req=req,
            mode=mode,
            verify=self._verify_ssl
        )
        if res["status"] != 0:
            raise Exception(parse_to_str(res))

        return res[constants.ConnectorKeys.MESSAGE]

    def post_pyapi_request(
            self, url: str,
            req: RequestContent = RequestContent(),
            mode: str = RequestMode.POST,
    ) -> Union[BaseModel, str]:
        return self.request(
            os.path.join(self._domain, constants.V1_API, url),
            req=req,
            mode=mode
        )

    def post_openapi_request(
            self, url: str,
            req: RequestContent = RequestContent(),
            mode: str = RequestMode.POST,
    ) -> dict:
        return self.request(
            os.path.join(self._domain, constants.OPEN_API, url),
            req=req,
            mode=mode,
        )


class PyAPI(Connector):
    def parse_data_information(
        self, name: str, study_format: str, data_paths: List[str]
    ) -> dict:
        return self.post_pyapi_request(
            url=constants.PARSE_DATA_URL,
            req=RequestContent(
                body_json={
                    constants.ConnectorKeys.DATA_NAME: name,
                    constants.ConnectorKeys.FORMAT: study_format,
                    constants.ConnectorKeys.DATA_PATH: data_paths,
                }
            )
        )


class OpenAPI(Connector):
    @property
    def info(self):
        return self.post_openapi_request(
            url=constants.INFO_URL,
            mode=RequestMode.GET,
        )

    @property
    def mounts(self):
        return self.post_openapi_request(
            url=constants.EXTERNAL_MOUNT_URL,
            mode=RequestMode.GET,
        )

    def list_s3(self, offset: int = 0, limit: int = 100):
        return self.post_openapi_request(
            url=constants.LIST_S3,
            req=RequestContent(
                data={
                    constants.ConnectorKeys.LIMIT: limit,
                    constants.ConnectorKeys.OFFSET: offset,
                }
            ),
            mode=RequestMode.POST,

        )

    @property
    def s3(self):
        return self.list_s3()

    @property
    def groups(self):
        return self.post_openapi_request(
            url=constants.GROUPS_URL,
            mode=RequestMode.GET,
        )

    def list_dir(self, path: str, ignore_hidden: bool = True):
        return self.post_openapi_request(
            constants.LIST_URL,
            req=RequestContent(
                data={
                    constants.ConnectorKeys.PATH: path,
                    constants.ConnectorKeys.IGNORE_HIDDEN: ignore_hidden,
                }
            )
        )

    def create_project(
        self,
        group_id: str,
        species: str,
        title: str,
        author: List[str] = None,
        create_type: int = constants.StudyType.SINGLECELL_STUDY_TYPE_NUMBER,
    ):
        if author is None:
            author = []
        return self.post_openapi_request(
            url=constants.CREATE_PROJECT_URL,
            req=RequestContent(
                body_json={
                    constants.ConnectorKeys.AUTHOR: author,
                    constants.ConnectorKeys.GROUP_ID: group_id,
                    constants.ConnectorKeys.SPECIES: species,
                    constants.ConnectorKeys.TITLE: title,
                    constants.ConnectorKeys.TYPE: create_type,
                }
            )
        )

    def list_project(
        self,
        group_id: str,
        species: str,
        limit: int = 50,
        offset: int = 0,
        active: int = constants.StudyStatus.PROCESSING_STATUS,
        compare: int = constants.StudyFilter.NOT_LARGER,
    ):
        return self.post_openapi_request(
            url=constants.LIST_PROJECT_URL,
            req=RequestContent(
                data={
                    constants.ConnectorKeys.GROUP_ID: group_id,
                    constants.ConnectorKeys.SPECIES: species,
                    constants.ConnectorKeys.LIMIT: limit,
                    constants.ConnectorKeys.OFFSET: offset,
                    constants.ConnectorKeys.ACTIVE: active,
                    constants.ConnectorKeys.COMPARE: compare,
                }
            )
        )

    def get_project_detail(self, project_id: str, limit: int = 50, offset: int = 0):
        return self.post_openapi_request(
            url=constants.DETAIL_PROJECT_URL,
            req=RequestContent(
                params={
                    constants.ConnectorKeys.KEY: project_id,
                    constants.ConnectorKeys.LIMIT: limit,
                    constants.ConnectorKeys.OFFSET: offset,
                }
            ),
            mode=RequestMode.GET,
        )

    def create_study(
        self,
        name: str,
        normalize: bool,
        project_id: str,
        submission_info: List[Dict],
        filter_params: Dict = None,
    ):
        if isinstance(filter_params, Dict) and filter_params:
            filter_str = json.dumps(filter_params)
        else:
            filter_str = ""
        if len(submission_info) == 0:
            raise ValueError("Submission data is empty")

        return self.post_openapi_request(
            url=constants.CREATE_STUDY_URL,
            req=RequestContent(
                body_json={
                    constants.ConnectorKeys.FILTER_PARAMS: filter_str,
                    constants.ConnectorKeys.GENOME_VERSION: constants.DEFAULT_GENE_VERSION,
                    constants.ConnectorKeys.NAME: name,
                    constants.ConnectorKeys.APPLY_NORMALIZE: normalize,
                    constants.ConnectorKeys.PROJECT_ID: project_id,
                    constants.ConnectorKeys.SUBMISSION_INFO: json.dumps(submission_info),
                    constants.ConnectorKeys.TOTAL_BATCH: len(submission_info),
                }
            )
        )

    def list_study(
        self,
        project_id: str,
        limit: int = 50,
        offset: int = 0,
        need_data: bool = False,
    ):
        return self.post_openapi_request(
            url=constants.LIST_STUDY_URL,
            req=RequestContent(
                params={
                    constants.ConnectorKeys.KEY: project_id,
                    constants.ConnectorKeys.LIMIT: limit,
                    constants.ConnectorKeys.OFFSET: offset,
                    constants.ConnectorKeys.NEED_DATA: need_data,
                }
            ),
            mode=RequestMode.GET,
        )

    def get_study_detail(self, study_id: str, limit: int = 50, offset: int = 0):
        return self.post_openapi_request(
            url=constants.DETAIL_STUDY_URL,
            req=RequestContent(
                params={
                    constants.ConnectorKeys.KEY: study_id,
                    constants.ConnectorKeys.LIMIT: limit,
                    constants.ConnectorKeys.OFFSET: offset,
                }
            ),
            mode=RequestMode.GET,
        )

    def list_public_project(
        self,
        group_id: str,
        species: str,
        limit: int = 50,
        offset: int = 0,
        active: int = constants.StudyStatus.PROCESSING_STATUS,
    ):
        return self.post_openapi_request(
            url=constants.LIST_PUBLIC_PROJECT_URL,
            req=RequestContent(
                body_json={
                    constants.ConnectorKeys.GROUP_ID: group_id,
                    constants.ConnectorKeys.SPECIES: species,
                    constants.ConnectorKeys.LIMIT: limit,
                    constants.ConnectorKeys.OFFSET: offset,
                    constants.ConnectorKeys.ACTIVE: active,
                }
            )
        )

    def upload_file(
        self, file_path: str,
        folder_name: str, upload_id: str,
        is_chunk: bool,
    ):
        with open(file_path, "rb") as file:
            resp = self.post_openapi_request(
                url=constants.UPLOAD_FILE_URL,
                req=RequestContent(
                    data={
                        constants.ConnectorKeys.UPLOAD_FOLDER_NAME: folder_name,
                        constants.ConnectorKeys.UPLOAD_UNIQUE_ID: upload_id,
                        constants.ConnectorKeys.UPLOAD_IS_CHUNK: is_chunk,
                    },
                    files={
                        constants.ConnectorKeys.UPLOAD_FILE_DATA: file,
                    }
                )
            )
        return resp

    def upload_chunk_start(self, folder_name: str, parent_is_file: int):
        return self.post_openapi_request(
            url=constants.UPLOAD_CHUNK_START_URL,
            req=RequestContent(
                body_json={
                    constants.ConnectorKeys.UPLOAD_FOLDER_NAME: folder_name,
                    constants.ConnectorKeys.UPLOAD_PARENT_IS_FILE: parent_is_file,
                }
            )
        )

    def upload_chunk_process(
        self,
        chunk_size: int,
        file_size: int,
        offset: int,
        file_name: str,
        folder_name: str,
        upload_id: str,
        path: str,
        sending_index: int,
        parent_is_file: int,
        file_data: list[str],
    ):
        return self.post_openapi_request(
            url=constants.UPLOAD_CHUNK_PROCESS_URL,
            req=RequestContent(
                data={
                    constants.ConnectorKeys.UPLOAD_FOLDER_NAME: folder_name,
                    constants.ConnectorKeys.UPLOAD_PARENT_IS_FILE: parent_is_file,
                    constants.ConnectorKeys.UPLOAD_CHUNK_SIZE: chunk_size,
                    constants.ConnectorKeys.UPLOAD_FILE_SIZE: file_size,
                    constants.ConnectorKeys.UPLOAD_OFFSET: offset,
                    constants.ConnectorKeys.UPLOAD_FILE_NAME: file_name,
                    constants.ConnectorKeys.UPLOAD_UNIQUE_ID: upload_id,
                    constants.ConnectorKeys.UPLOAD_PATH: path,
                    constants.ConnectorKeys.UPLOAD_SENDING_INDEX: sending_index,
                },
                files={
                    constants.ConnectorKeys.UPLOAD_FILE_DATA: file_data,
                }
            )
        )

    def upload_chunk_merge(
        self,
        total_chunk: int,
        file_name: str,
        folder_name: str,
        upload_id: str,
        path: str,
        parent_is_file: int,
        move_to_parent: bool,
    ):
        return self.post_openapi_request(
            url=constants.UPLOAD_CHUNK_MERGE_URL,
            req=RequestContent(
                body_json={
                    constants.ConnectorKeys.UPLOAD_FOLDER_NAME: folder_name,
                    constants.ConnectorKeys.UPLOAD_PARENT_IS_FILE: parent_is_file,
                    constants.ConnectorKeys.UPLOAD_TOTAL_CHUNK: total_chunk,
                    constants.ConnectorKeys.UPLOAD_FILE_NAME: file_name,
                    constants.ConnectorKeys.UPLOAD_UNIQUE_ID: upload_id,
                    constants.ConnectorKeys.UPLOAD_PATH: path,
                    constants.ConnectorKeys.UPLOAD_MOVE_TO_PARENT: move_to_parent,
                }
            )
        )

    def upload_folder_finish(self, folder_name: str, upload_id: str):
        return self.post_openapi_request(
            url=constants.UPLOAD_FOLDER_FINISH_URL,
            req=RequestContent(
                data={
                    constants.ConnectorKeys.UPLOAD_FOLDER_NAME: folder_name,
                    constants.ConnectorKeys.UPLOAD_UNIQUE_ID: upload_id,
                },
            )
        )
