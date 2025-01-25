# CanvasRobot
Library which uses
[Canvasapi](https://canvasapi.readthedocs.io/en/stable/getting-started.html)
(minimally patched to allow more flexible user search)
to provide a CanvasRobot class for GUI and commandline use.
You can install canvasrobot and urltransform (special edition 
to translate video urls in Canvas pages) 
using [UV](https://docs.astral.sh/uv/getting-started/installation/)
Tip: use `brew` to install on macOS and `winget` on Windows. Check if the 
path is correct, after reopening terminal/Powershell

``` commandline
uv tool install canvasrobot

canvasrobot --help
urltransform --help
```

## Uses 
- [CanvasAPI](https://canvasapi.readthedocs.io/en/stable/getting-started.html) 
- rich
- rich_click
- keyring (safe store for API key)
- pydal (local database)
- pywebview (HTML reporting)
- [opt] pymemcache (install to add caching canvas interaction)

## Used 
In word2quiz library.
(Not yet ready for general use...)

## Examples
```Python
import rich
import canvasrobot as cr

if __name__ == '__main__':

    console = rich.console.Console(width=160, force_terminal=True)

    robot = cr.CanvasRobot(reset_api_keys=False,
                           console=console)

    # robot.update_database_from_canvas()
    robot.create_folder_in_all_courses('Tentamens')



    # result = robot.enroll_in_course("", 4472, 'u752058',
    # 'StudentEnrollment') #  (enrollment={'type': 'StudentEnrollment'}
    
    # user = robot.search_user('u752058')
    # print(user)
    # if not user:
    #   print(robot.errors)

    #COURSE_ID = 9999  # test course
    #result = robot.create_folder_in_course_files(COURSE_ID, 'Tentamens')

    # print(robot.course_metada(COURSE_ID))
    # print(robot.unpublish_folderitems_in_course(COURSE_ID,
    #                                            foldername,
    #                                            files_too=True))

    #course = robot.get_course(COURSE_ID)
    # tab = robot.get_course_tab_by_label(COURSE_ID, "Files")
    # print(tab.visibility)

    # for course_id in (COURSE_ID, COURSE_ID2):
    #     result = robot.create_folder_in_course_files(course_id, 'Tentamens')

    # result = robot.unpublish_subfolder_in_all_courses(foldername,
    #                                                  files_too=True,
    #                                                  check_only=True)
    # if course_ids_missing_folder:
    #    logging.info(f"Courses with missing folder {foldername}: {course_ids_missing_folder}")


    # QUIZZES -----------------------------

    # filename = 'Q_A.docx'
    # robot.create_quizzes_from_document(filename=filename,
    #                                    course_id=COURSE_ID,
    #                                    question_format='Vraag {}. Vertaal:',
    #                                    adjust_fontsize=True,
    #                                    testrun=False
    #                                    )
```


[![PyPI version](https://badge.fury.io/py/canvasrobot.svg)]
