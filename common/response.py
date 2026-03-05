from rest_framework.response import Response
from rest_framework.status import is_success
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

class StandardAPIResponse(Response):
    """
    Standard API Response Class as per HelixBeat Standard API Guidelines
    """

    def __init__(
        self,
        data=None,
        status=None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
        context=None,
        message=None,  # <- NEW PARAM
    ):
        standard_response_data = {
            "status": False if status is None else is_success(status),
        }

        # Add message always (if provided)
        if message:
            standard_response_data["message"] = message

        if standard_response_data["status"]:
            # SUCCESS RESPONSE
            standard_response_data["data"] = data

            export_context = None
            import_context = None

            if context:
                export_context = context.get("report_code")
                import_context = context.get("import_config_code")

            if export_context or import_context:
                meta_definition = {}
                if export_context:
                    meta_definition["export"] = {**context}

                if import_context:
                    meta_definition["import"] = {
                        "context": import_context,
                    }

                standard_response_data["meta_definition"] = meta_definition

        else:
            # ERROR RESPONSE
            standard_response_data["errors"] = data

        super().__init__(
            standard_response_data,
            status,
            template_name,
            headers,
            exception,
            content_type,
        )

    @classmethod
    def from_response(cls, response_obj, message=None):
        if isinstance(response_obj, StandardAPIResponse):
            return response_obj
        return StandardAPIResponse(
            data=response_obj.data,
            message=message,
            status=response_obj.status_code,
            headers=response_obj.headers,
        )


class StandardPageNumberPagination(PageNumberPagination):
    page_size_query_param = "per_page"

    def get_paginated_response(self, data, context=None):
        return StandardAPIResponse(
            data={
                "values": data,
                "pagination": {
                    "page": self.page.number,
                    "per_page": self.page.paginator.per_page,
                    "total": self.page.paginator.count,
                    "more": self.page.has_next(),
                },
            },
            status=status.HTTP_200_OK,
            context=context,
        )