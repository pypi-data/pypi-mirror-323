# Handler Reviews #

## What is this? ##
The module allows process reviews of your clients by tamplates or AI.

## Quick Guide ##
The module is based on the following structure:

    
    handler = ReviewsHandlerProvider()
    gpt_handler = handler.fetch_handler(handler_type=HandlerType.GPTHANDLER, api_key=api_key_gpt)
    template_handler = handler.fetch_handler(handler_type=HandlerType.TEMPLATEHANDLER)
    
Which Python provides by standard.

----------

### Using ###


Using the library is as simple and convenient as possible:

Let's import it first:
First, import everything from the library (use the `from `...` import *` construct).

    handler = ReviewsHandlerProvider()
    gpt_handler = handler.fetch_handler(handler_type=HandlerType.GPTHANDLER, api_key=api_key_gpt)
    template_handler = handler.fetch_handler(handler_type=HandlerType.TEMPLATEHANDLER)

#Get your data like name_client, review, grade, return_amount_tokens

response_gpt = gpt_handler.get_response(name_client, review, grade, return_amount_tokens)
response_tamplate = template_handler.get_response(name_client, grade)

----------


## Developer ##
My site: [link](https://github.com/Azakaim/) 
