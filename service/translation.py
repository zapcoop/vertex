from modeltranslation.translator import TranslationOptions, translator

from .models import Team, EmailTemplate


class TeamTranslationOptions(TranslationOptions):
    fields = ('name',)


class EmailTemplateTranslationOptions(TranslationOptions):
    fields = ('template_name', 'subject', 'heading', 'plain_text', 'markdown',)


translator.register(Team, TeamTranslationOptions)
translator.register(EmailTemplate, EmailTemplateTranslationOptions)
