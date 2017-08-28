import email
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language, override
from django.template import Template, Context, loader

import markdown
import bleach

from noss.models import AbstractDatedModel

BASE_TEMPLATE_PREFIX = 'email_templates/base_service_email'

MISSING_TRANSLATION_MESSAGE = ("Can't render a bilingual version of "
                               "EmailTemplate {} because a translation is missing. "
                               "The following translations were available: {}")

__author__ = 'jsenecal'


class EmailTemplate(AbstractDatedModel):
    """
    Since these are more likely to be changed than other templates, we store
    them in the database.
    This means that an admin can change email templates without having to have
    access to the filesystem.
    """
    slug = models.SlugField(unique=True)

    template_name = models.CharField(
            _('Template Name'),
            max_length=100,
    )

    subject = models.CharField(
            _('Subject'),
            max_length=100,
            help_text=_('This will be prefixed with "[ticket.ticket] ticket.title"'
                        '. We recommend something simple such as "(Updated") or "(Closed)"'
                        ' - the same context is available as in plain_text, below.'),
    )

    heading = models.CharField(
            _('Heading'),
            max_length=100,
            help_text=_('In HTML e-mails, this will be the heading at the top of '
                        'the email - the same context is available as in plain_text, '
                        'below.'),
    )

    plain_text = models.TextField(
            _('Plain Text'),
            help_text=_('The context available to you includes {{ ticket }}, '
                        '{{ department }}, and depending on the time of the call: '
                        '{{ resolution }} or {{ comment }}.'),
    )

    markdown = models.TextField(
            _('Markdown'),
            help_text=_('The same context is available here as in plain_text, '
                        'above. The markdown will be rendered as HTML in the e-mail'),
    )

    def render_html(self, context):
        if not get_language():  # no language set
            return self.render_html_bilingual(context)
        else:
            inner_template = markdown.markdown(bleach.clean(self.markdown))
            outer_template = loader.get_template('email_templates/base_service_email.md')
            outer_context = Context({
                'inner_template': Template(inner_template).render(context),
                'language_code': self.language_code
            })

        return outer_template.render(outer_context)

    def render_plain(self, context):
        if not get_language():  # no language set
            return self.render_plain_bilingual(context)
        else:
            inner_template = Template(self.get_plaintext()).render(context)

            outer_template = loader.get_template('email_templates/base_service_email.txt')
            outer_context = Context({
                'inner_template': inner_template,
                'language_code': self.language_code
            })

        return outer_template.render(outer_context)

    def render_plain_bilingual(self, context):

        with override('fr'):
            inner_template_fr = Template(self.get_plaintext()).render(context)

        with override('en'):
            inner_template_en = Template(self.get_plaintext()).render(context)

        outer_context = Context({
            'inner_template_fr': inner_template_fr,
            'inner_template_en': inner_template_en
        })
        outer_template = loader.get_template('email_templates/base_service_email_bilingue.txt')
        return outer_template.render(outer_context)

    def render_html_bilingual(self, context):

        inner_template_fr = sanitize_and_render_markdown(self.markdown_fr)
        inner_template_en = sanitize_and_render_markdown(self.markdown_en)

        outer_context = Context({
            'inner_template_fr': inner_template_fr,
            'inner_template_en': inner_template_en
        })

        outer_template = loader.get_template('email_templates/base_service_email_bilingue.md')
        return outer_template.render(outer_context)

    @property
    def bilingual_subject(self):
        return self.subject_fr + ' | ' + self.subject_en

    def send_service_email(self, context, from_mailbox, to, cc,
                           in_reply_to_message=None, reply_to_address=None):
        subject = build_subject(self.subject, context)
        email_message = EmailMultiAlternatives(
                from_email=from_mailbox.from_email,
                to=to,
                cc=cc,
                subject=subject,
                body=self.render_plain(context),
                reply_to=reply_to_address
        )
        email_message.attach_alternative(self.render_html(context), 'text/html')

        if in_reply_to_message:
            in_reply_to_message.reply(
                email_message)  # sets in-reply-to header & records this outgoing message and sends it
        else:
            email_message.send()
            from_mailbox.record_outgoing_message(
                    email.message_from_string(
                            email_message.message().as_string()
                    )
            )

    def send_service_email_bilingual(self, context, from_mailbox, to, cc,
                                     in_reply_to_message=None, reply_to_address=None):
        subject = build_subject(self.bilingual_subject, context)
        email_message = EmailMultiAlternatives(
                from_email=from_mailbox.from_email,
                to=to,
                cc=cc,
                subject=subject,
                body=self.render_plain_bilingual(context),
                reply_to=reply_to_address
        )
        email_message.attach_alternative(self.render_html_bilingual(context), 'text/html')

        if in_reply_to_message:
            in_reply_to_message.reply(
                email_message)  # sets in-reply-to header & records this outgoing message and sends it
        else:
            email_message.send()
            from_mailbox.record_outgoing_message(
                    email.message_from_string(
                            email_message.message().as_string()
                    )
            )

    def get_plaintext(self):
        """If the plain_text field is empty, return the contents of the markdown field instead.
        """
        if self.plain_text:
            return self.plain_text
        else:
            return self.markdown

    def __str__(self):
        return u'%s' % self.template_name

    class Meta:
        verbose_name = _('e-mail template')
        verbose_name_plural = _('e-mail templates')
        app_label = 'service'


# def get_plaintext(obj):
#     """If the plain_text field is empty, return the contents of the markdown field instead.
#     """
#     plain_text = obj.plain_text
#     if plain_text:
#         return plain_text
#     else:
#         return obj.markdown


def build_subject(subject, context):
    if 'ticket' in context:
        ticket = context['ticket']
        subject_prefix = ' '.join((ticket.ticket_id, ticket.title,))
    else:
        subject_prefix = ''
    return subject_prefix + subject


def sanitize_and_render_markdown(source):
    return markdown.markdown(bleach.clean(source))
