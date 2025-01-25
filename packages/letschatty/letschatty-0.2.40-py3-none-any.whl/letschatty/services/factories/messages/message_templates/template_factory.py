
from typing import Dict, List
from .....models.messages.message_templates import WhatsappTemplate, TemplateFormForFrontend, TemplateComponentForPayload, TemplateRequestPayload, TemplateDataFromFrontend
from .....models.messages.message_templates.template_for_frontend_use import ParameterFormForFrontend, ParametersFromFrontend
from .....models.messages.message_templates.payload_for_sending_template import ComponentForPayload, TemplateComponentForPayload, TemplateRequestPayload, PositionalParameterForPayload, NamedParameterForPayload
from .....models.messages.message_templates.raw_meta_template import ParameterFormat
import logging
logger = logging.getLogger(__name__)

class TemplateFactory:
    
    @staticmethod
    def build_template_form_for_frontend_only_body_and_parameters(template: WhatsappTemplate) -> TemplateFormForFrontend:
        if template.parameter_format == ParameterFormat.NAMED:
            parameters = [ParameterFormForFrontend(id=parameter.param_name, example=parameter.example) for parameter in template.body_component.example.body_text_named_params]
            return TemplateFormForFrontend(name=template.name, text=template.body_component.text, parameters=parameters)
        
        if template.parameter_format == ParameterFormat.POSITIONAL:
            parameters = [ParameterFormForFrontend(id=str(index), example=parameter) for index, parameter in enumerate(template.body_component.example.body_text[0])]
            logger.debug(f"Positional Parameters: {parameters}")
            return TemplateFormForFrontend(name=template.name, text=template.body_component.text, parameters=parameters)
        
        return TemplateFormForFrontend(name=template.name, text=template.body_component.text, parameters=[])
    @staticmethod
    def build_template_payload(template: WhatsappTemplate, template_data : TemplateDataFromFrontend) -> TemplateComponentForPayload:  
        template_data.body = TemplateFactory.replace_parameters_in_body(template.body_component.text, template_data.parameters)
        
        if template.parameter_format == ParameterFormat.NAMED:
            parameters = NamedParameterForPayload.from_template_parameters(template_data.parameters)
            components = [ComponentForPayload(type=template.body_component.type, parameters=parameters)]
        elif template.parameter_format == ParameterFormat.POSITIONAL:
            parameters = PositionalParameterForPayload.from_template_parameters(template_data.parameters)
            components = [ComponentForPayload(type=template.body_component.type, parameters=parameters)]
        else:
            components = []
            
        return TemplateComponentForPayload(name=template.name, language={"code": template.language}, components=components)
    
    @staticmethod
    def build_template_request_payload(template_data : TemplateDataFromFrontend, template : WhatsappTemplate) -> TemplateRequestPayload:
        template_payload = TemplateFactory.build_template_payload(template=template, template_data=template_data)
        return TemplateRequestPayload(messaging_product="whatsapp", recipient_type="individual", to=template_data.phone_number, type="template", template=template_payload)

    @staticmethod
    def replace_parameters_in_body(body : str, parameters : List[ParametersFromFrontend]) -> str:
        for parameter in parameters:
            body = body.replace(f"{{{parameter.id}}}", parameter.text)
        return body