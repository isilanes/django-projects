import os
import sys

if __name__ == "__main__":
    try:
        import WebProjects
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WebProjects.settings")
    except:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WebProjects.WebProjects.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
