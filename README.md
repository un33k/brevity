# Brevity
A powerful multimedia-rich framework that aims at making online publishing very simple

[![Brevity](https://img.youtube.com/vi/NQXxNyJmBr8/maxresdefault.jpg)](http://youtu.be/NQXxNyJmBr8)

# Details
**Brevity** is a multimedia publishing framework, elegantly designed and built around one guiding principle: **Quality of Experience** for its users. Users are both publishers and readers.

**Quality of Experience** is achieved through **simplicity**, **security** and **performance**. With Brevity, simplicity is transforming a thought into a stunning online article in less than 5 minutes. With Brevity, security is having the peace of mind, knowing that all necessary measures are taken to ensure the security of your data . With Brevity, performance is reaching thousands to millions of readers within seconds of publishing, knowing that they will enjoy your creativity no matter what device they’re on.

Your personal time and energy are valuable and finite resources. As a publisher, you need to invest your resources into those things that make you, who you are. Brevity takes care of the technical details allowing you to create to your maximum potential. And best of all, “you” can be anybody such as:

- a **blogger** looking to write about your day-to-day personal or professional interests and activities
- a **real estate agent** looking to create stunning, media-rich listings for the properties you are buying or selling
- an **online reviewer** looking to conveniently share your thoughts about products and/or services with readers on the web
- a **travel agent** looking to review destinations and excite your potential clients with dreams of escape
- a **baker** or a **chef** looking to publish your recipes and make them available to your potential customers
- Or **anyone** with a passion for telling your story to the world.

Use your **intellect** and **passion** on what is really important to you and let **Brevity** take care of everything else.


# Demo
Visit [simplyfound.com](https://simplyfound.com), create an account and take brevity for a spin.


# Development

```bash
# clone our repository (--depth 1 only gets the last .git commit history)
git clone --depth 1 https://github.com/un33k/brevity.git

# change directory to our repo
cd brevity

# change to the development branch
git checkout development

# add required global libraries
pip install -r env/reqs/dev.txt

# make a copy of the seekrets.json file
cp seekrets-example.json seekrets.json
# make the required changes in seekrets.json for your own setup

# setup your development env
export DJANGO_SERVER_TYPE='DEVELOPMENT'

# prepare your `sqlite` database for your first run
bin/dev/manage.py migrate

# run your local development server
bin/dev/manage.py runserver_plus 0.0.0.0:8080

# point your browser to localhost:8080

# login and start looking around (e.g. create articles)
# superuser username is found in `superuser_username` in the seekrets.json file
# superuser password is `hello` -- development ONLY
```


# Deployment
You can adapt the development steps and modify as per your deployment needs.

Alternative, Brevity can be deployed for you.
Please contact us at [neekware.com](http://neekware.com)
