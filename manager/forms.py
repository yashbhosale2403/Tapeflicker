from django import forms
from courses.models import Course, Category, Module, Lesson, LessonResource
from core.models import Event

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'slug', 'category', 'instructor', 'price', 'discount_price', 'difficulty', 'description', 'learning_outcomes', 'prerequisites', 'thumbnail', 'banner', 'is_featured', 'is_locked']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition', 'placeholder': 'Course Title'}),
            'slug': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition', 'placeholder': 'course-slug'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition'}),
            'instructor': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition'}),
            'discount_price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition'}),
            'difficulty': forms.Select(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition', 'rows': 4}),
            'learning_outcomes': forms.Textarea(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition', 'rows': 3}),
            'prerequisites': forms.Textarea(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition', 'rows': 2}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-mainaccent bg-mainpanel border-mainborder rounded focus:ring-mainaccent'}),
            'is_locked': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-mainaccent bg-mainpanel border-mainborder rounded focus:ring-mainaccent'}),
            'thumbnail': forms.FileInput(attrs={'class': 'w-full text-sm text-mainmuted file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-mainaccent file:text-black hover:file:bg-cyan-400'}),
            'banner': forms.FileInput(attrs={'class': 'w-full text-sm text-mainmuted file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-mainaccent file:text-black hover:file:bg-cyan-400'})
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'event_type', 'description', 'date', 'registration_link', 'banner', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition'}),
            'event_type': forms.Select(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition', 'rows': 4}),
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition'}),
            'registration_link': forms.URLInput(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition'}),
            'banner': forms.FileInput(attrs={'class': 'w-full text-sm text-mainmuted file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-mainaccent file:text-black hover:file:bg-cyan-400'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-mainaccent bg-mainpanel border-mainborder rounded focus:ring-mainaccent'}),
        }


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition', 'placeholder': 'Module title'}),
            'order': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition', 'min': 0}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['module', 'title', 'video_url', 'duration', 'order', 'description', 'notes', 'resource_file', 'is_preview', 'is_published']
        widgets = {
            'module': forms.Select(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition'}),
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition', 'placeholder': 'Lesson title'}),
            'video_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition', 'placeholder': 'https://www.youtube.com/watch?v=...'}),
            'duration': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition', 'placeholder': 'e.g. 12:30'}),
            'order': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition', 'min': 0}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition', 'rows': 3}),
            'resource_file': forms.FileInput(attrs={'class': 'w-full text-sm text-mainmuted file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-mainaccent file:text-black hover:file:bg-cyan-400'}),
            'is_preview': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-mainaccent bg-mainpanel border-mainborder rounded focus:ring-mainaccent'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-mainaccent bg-mainpanel border-mainborder rounded focus:ring-mainaccent'}),
        }


class LessonResourceForm(forms.ModelForm):
    class Meta:
        model = LessonResource
        fields = ['title', 'file', 'external_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition', 'placeholder': 'Resource title'}),
            'file': forms.FileInput(attrs={'class': 'w-full text-sm text-mainmuted file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-mainaccent file:text-black hover:file:bg-cyan-400'}),
            'external_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2 bg-mainpanel border border-mainborder rounded-lg text-white focus:outline-none focus:border-mainaccent transition', 'placeholder': 'https://...'}),
        }
