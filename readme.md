# Flask Mailhide

A replacement of Google's [Mailhide](https://www.google.com/recaptcha/mailhide/d) (deprecated due to the shutdown of reCAPTCHA v1) using [reCAPTCHA](https://developers.google.com/recaptcha/intro) v2. 


## Usage

1. [Sign up](http://www.google.com/recaptcha/admin) for your own reCAPTCHA key from Google. Both regular and invisible keys are supported.
2. Replace `<site_key>` in `home.html` and `SECRET` in `app.py` with your own. 
4. Include a link to your application in the web page where your masked email address is shown. 

Example:

```html
<p><a href="https://example.com" onclick="window.open('https://example.com', '', 'toolbar=0,scrollbars=0,location=0,statusbar=0,menubar=0,resizable=0,width=500,height=300'); return false;" title="Reveal this e-mail address">foo&hellip;</a>@github.com (Click to reveal email address)</p>
```


## Notes

The code uses `www.recaptcha.net` instead of `www.google.com` to enable access from places where Google is blocked. See the [FAQ](https://developers.google.com/recaptcha/docs/faq#can-i-use-recaptcha-globally) of reCAPTCHA for details on global access. 
