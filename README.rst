django-multiforeignkey
======================

Django ForeignKey that links to one of several specified models:

.. code:: python

	class Comment(models.Model):
		user = models.ForeignKey(User)
		text = models.TextField()

		# users may leave comments for blog posts, articles or votings
		object = MultiForeignKey(Post, Article, Voting)


Unlike ``GenericForeignKey``, the field uses native database foreign keys and provides maximum speed and reliability.


WARNING
=======

**This is a preliminary alpha version which most probably doesn't fully work as advertised. I had to publish it unfinished because I had to use it in my project.**


Installation
============

::

	pip install django-multiforeignkey


Usage
=====

Add ``multiforeignkey`` to ``INSTALLED_APPS``:

.. code:: python

	# settings.py

	INSTALLED_APPS = [
		...
		'multiforeignkey',
	]


Add a field to your models:

.. code:: python

	# comments/models.py

	from multiforeignkey.models import MultiForeignKey

	class Comment(models.Model):
		user = models.ForeignKey(User)
		text = models.TextField()

		# users may leave comments for blog posts, articles or votings
		object = MultiForeignKey(Post, Article, Voting)


Create the corresponding database tables:

.. code:: bash

	./manage.py makemigrations && ./manage.py migrate


Use the new field as if it were a real database field:

.. code:: python

	comment = Comment.objects.filter(object=post)
	assert comment.object is post
	comment.object = voting
	assert comment.object is voting
	comment.save()


or use specific subfields:

.. code:: python

	comment = Comment.objects.filter(post=post)
	assert comment.post is post
	assert comment.article is None
	assert comment.voting is None
	comment.voting = voting
	assert comment.post is None
	assert comment.article is None
	assert comment.voting is voting
	comment.save()
