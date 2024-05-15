
# Ejection to a Django app

One of the key features of HStream is not having to start over when your project outgrows the linear script structure of HStream. This out growing could be due to needing to implement more complex authentication, more custom user flows or any number of other issues I have faced in building real world PoC's with Streamlit in the past.

Whatever it may be, when you do (hopefully) reach that point just run:

`hstream eject`

`python manage.py runserver` <- this is now running a full fledge Django instance you can edit as you please :)

We'll put your current working app in your directory as a traditional Django app for you to add more routes onto the working HStream endpoint.

*Caveat:* the HStream part of the server won't follow a typical Django web app structure, but you can go ahead and develop the rest of your service in traditional Django fashion.
