from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect


def cookieconsent_context(request: HttpRequest):
    """
    The fields `title`, `sub_title`, `description`, and `final_note` provide
    the means to compose a detailed message for the form presented to the 
    client. In contrast, the `options` field contains a comprehensive list
    of all types of cookies that can be managed with this package throughout
    the Django project.

    The `type` and `description` fields provide a general overview to inform
    the client of their intended function.

    In contrast, the `category` field contains values that will be stored in
    the browser's cookie as `userconsent=<category1>,<category2>`, with the 
    `str(category)` values concatenated by a comma (`,`). It is crucial to
    ensure that any object passed returns a *valid* `str`.

    + The `if_declined` field can take on three potential values: `abort`,
    `continue`, and `request`. This functionality enables the developer to
    respond based on the user's decision regarding the acceptance of specific
    types of cookies.

        - `abort`: If the client opts out of this type of cookie, a 
        `redirection_message` will be displayed, and the request will be redirected
        to `redirect_path`.

        - `continue`: This directive allows the request to proceed as if everything
        is in order.

        - `request`: With this option, the request will be redirected to 
        `redirect_path`, and a `redirection_message` will be shown.
    """
    return settings.COOKIECONSENT


def cookie_if_consent_or_action(
    request: HttpRequest, response: HttpResponse, category, *args, **kwargs
):
    """
    This function helps making sure if the user has permitted particular kind of
    cookie to be stored on their machine. For Cookie, kwargs can be passed as
    provided by `HttpResponse.set_cookie` by Django at link 
    https://docs.djangoproject.com/en/5.1/ref/request-response/#django.http.HttpResponse.set_cookie.
        Args:
        request (_type_): to flash message,
        response (HttpResponse): to set cookie,
        category : same as defined in setting.COOKIECONSENT["options"],
        *args: positional arguments,
        **kwargs: keyword arguments

    Returns:
        _type_: HttpResponse
    """
    userconsent = request.COOKIES.get("userconsent", None)
    if str(category) in str(userconsent):
        response.set_cookie(*args, **kwargs)
        return response
    else:
        for item in settings.COOKIECONSENT["options"]:
            if item["category"] == category:
                if item["if_declined"] == "abort":
                    messages.info(request, item["redirection_message"])
                    return redirect(item["redirect_path"])
                elif item["if_declined"] == "continue":
                    return response
                elif item["if_declined"] == "request":
                    messages.info(request, item["redirection_message"])
                    return redirect(item["redirect_path"])
