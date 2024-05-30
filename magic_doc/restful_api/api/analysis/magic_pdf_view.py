import requests
from flask import request, current_app
from flask_restful import Resource
from marshmallow import ValidationError
from pathlib import Path
from magic_doc.pdf_transform import DocConverter, S3Config
from .serialization import MagicPdfSchema
from magic_doc.restful_api.common.custom_response import generate_response
from loguru import logger


class MagicPdfView(Resource):
    @logger.catch
    def post(self):
        magic_pdf_schema = MagicPdfSchema()
        try:
            params = magic_pdf_schema.load(request.get_json())
        except ValidationError as err:
            return generate_response(code=400, msg=err.messages)
        pdf_path = params.get('pageUrl')
        # pdf解析
        file_name = str(Path(pdf_path).stem)
        pf_path = f"/tmp/{file_name}.txt"
        app_config = current_app.config
        if pdf_path.startswith("s3://"):
            s3_config = S3Config(app_config["S3AK"], app_config["S3SK"], app_config["S3ENDPOINT"])
            docconv = DocConverter(s3_config)
        elif pdf_path.startswith("http://") or pdf_path.startswith("https://"):
            download_pdf = requests.get(pdf_path, stream=True)
            pdf_path = f"{current_app.static_folder}/pdf/{file_name}.pdf"
            with open(pdf_path, "wb") as wf:
                wf.write(download_pdf.content)
            docconv = DocConverter(None)
        else:
            docconv = DocConverter(None)
        result = docconv.convert_to_mid_result(pdf_path, pf_path, 60)
        return generate_response(data=result, markDownUrl=pdf_path)
