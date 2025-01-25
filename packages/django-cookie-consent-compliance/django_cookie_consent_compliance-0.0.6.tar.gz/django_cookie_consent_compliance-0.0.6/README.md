# django-cookie-consent-compliance

## A deterministic package allowing user consent implication for monitoring cookie on django project

### Index

- [Usability](#usability)
- [Configuration](#configuration)
- [Using in Project](#using-in-project)


## <a name="usability"></a>Usability
This package facilitates compliance with the new privacy policy by requiring the disclosure of all cookies stored on the user's device, thereby empowering users to opt-in or opt-out of specific types of cookies. Additionally, it enables site owners to respond appropriately to the preferences expressed by their clients. 

The implementation process is straightforward, as detailed in the documentation provided below.

## <a name="configuration"></a>Configuration

Initially, it is essential to establish the `COOKIECONSENT` option within the `[root_app]/settings.py` file of the project.


```sh
COOKIECONSENT = {
    "title": ,
    "sub_title":,
    "description":,
    "final_note": ,
    "options": [
        {
            "type": ,
            "description": ,
            "category":,
            "if_declined":,
        },
    ],
}
```

This component enables the customization of the appearance of notifications requesting cookie consent and facilitates the inclusion of relevant categories as required by the project.

The fields `title`, `sub_title`, `description`, and `final_note` provide the means to compose a detailed message for the form presented to the client. In contrast, the `options` field contains a comprehensive list of all types of cookies that can be managed with this package throughout the Django project. 

For illustration purposes, a sample is provided below.

```sh
COOKIECONSENT = {
    "title": "🍪 Cookie Time! 🍪",
    "sub_title": "We use cookies to make your experience at App even better! 🎭",
    "description": "By clicking “Got It!” or continuing to browse our app, you’re accepting our use of cookies (no, not the chocolate chip ones, unfortunately 😅). Here's how we use them:",
    "final_note": "💡 Remember: You can change your cookie preferences anytime via your browser settings if you're not fully on board. But don't worry, the cookies we use are harmless — no magical powers or teleportation here, promise! 😉",
    "options": [
        {
            "type": "Performance Cookies",
            "description": "We use these to check how well the app is doing. They help us improve the experience, so you can enjoy our digital theatre even more.",
            "category":  ,
            "if_declined": "continue",
        },
        {
            "type": "Marketing Cookies",
            "description": "Think of these as the set designers. They remember your preferences, like your language or favorite settings, so you don’t have to keep telling us every time you return.",
            "category":  ,
            "if_declined": "request",
            "redirect_path": "login",
            "redirection_message": "Make sure to select appropriate cookie to continue further.",
        },
        {
            "type": "Analytics Cookies",
            "description": "These help us see how you’re enjoying the show. We gather data to make the app better, so you’ll keep coming back for the encore. 🎤",
            "category":  ,
            "if_declined": "abort",
            "redirect_path": "login",
            "redirection_message": "Your request can't be processed further because some cookies are not present.",
        },
    ],
}
```


The `type` and `description` fields provide a general overview to inform the client of their intended function.

In contrast, the `category` field contains values that will be stored in the browser's cookie as `userconsent=<category1>,<category2>`, with the `str(category)` values concatenated by a comma (`,`). It is crucial to ensure that any object passed returns a *valid* `str` containing letters and numbers only (no meta characters).

+ The `if_declined` field can take on three potential values: `abort`, `continue`, and `request`. This functionality enables the developer to respond based on the user's decision regarding the acceptance of specific types of cookies.
    - `abort`: If the client opts out of this type of cookie, a `redirection_message` will be displayed, and the request will be redirected to `redirect_path`.

    - `continue`: This directive allows the request to proceed as if everything is in order.

    - `request`: With this option, the request will be redirected to `redirect_path`, and a `redirection_message` will be shown.

## <a name="using-in-project"></a>Using in project

### 1. To install this package, execute the command `pip install django-cookie-consent-compliance`.


### 2. Insert the cookie notification defining object `COOKIECONSENT` into `<root-app>/settings.py` as previously indicated.

    - Add `cookieconsent.cookieconsent_context` in `TEMPLATES["OPTIONS"]["context_processors"]`.

### 3. Add following template in `base.html`. `id` and `class` of element can be added/updated as per necessity.

```html
   {% if not request.COOKIES.userconsent %}
    <div id="cookieconsent-container">
        <form action="#" method="POST" id="cookieconsent">
            {% csrf_token %}
            <h3>{{ title }}</h3>
            <p>{{ sub_title }}</p>
            <br />
            <p>{{ description }}</p>
            <table>
                {% for opt in options %}
                <tr>
                    <td><label for=""><b>{{opt.type}}:</b>
                            {{opt.description}}</label>
                    </td>
                    <td><input type="checkbox" value={{opt.category}}></td>
                </tr>
                {% endfor %}
            </table>
            <p>{{ final_note }}</p>
            <button type="submit">Submit</button>
        </form>
    </div>
    <script>
        let form = document.getElementById("cookieconsent");
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            let choices = [];
            Object.values(form).forEach(i => {
                if (i.localName == "input" && !["hidden", undefined].includes(i.type) && i.checked) {
                    choices.push(i.value);
                }
            });
            document.cookie = `userconsent=${choices ? choices : ""}; Max-Age=2592000; path=/; SameSite=strict; Secure;`;
            document.getElementById("cookieconsent-container").style.display = "none";
        })
    </script>
    {% endif %}
```

### 4. In the `views.py` where it is necessary to set a cookie, utilize as following:

```py
from cookieconsent import cookie_if_consent_or_action
def view_function(request):
    response = cookie_if_consent_or_action(request:HttpRequest, response: HttpResponse, category1, "lang", value="en")
    response = cookie_if_consent_or_action(request:HttpRequest, response: HttpResponse, category2, "theme", value="auto")
    return response
```

If all types of cookies are utilized in a view, last `redirect_path` with cumulative `redirection_message`.

`cookie_if_consent_or_action` function utilizes Django's `HttpResponse.set_cookie` method, allowing for the inclusion of all valid `kwargs`.

[Sample Live Project](https://py2s.pythonanywhere.com/)
