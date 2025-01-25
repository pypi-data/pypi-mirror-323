from datetime import datetime
import os
from pydal import DAL, Field, validators  # type: ignore
import yaml
import logging
import logging.config

from attrs import define
import keyring
# for UI use rich or tkinter
from rich.prompt import Prompt
from tkinter import simpledialog


# noinspection PyClassHasNoInit
@define
class CanvasConfig:
    """"
    save the urls and API_key in a safe space using
    keyring (works on macOS and Windows)"""
    namespace = "canvasrobot"
    gui_root: object = None
    reset_api_keys: bool = False
    url: str = ""
    api_key: str = ""
    admin_id: int = 0
    api_fields = (
        dict(msg="Enter your Canvas URL (like https://[name].instructure.com)",
             key="url"),
        dict(msg="Enter your Canvas APi Key",
             key="api_key"),
        dict(msg="Enter your Canvas Admin id or 0 ",
             key="admin_id"),
    )

    # start_month = 8

    def __attrs_post_init__(self):
        if self.reset_api_keys:
            self.reset_keys()
        self.get_values()

    def get_values(self):
        """ ask for canvas url, api key and admin_id , uses keyring to
        store them in a safe space"""

        for field in self.api_fields:
            value = self.get_value(field["msg"], field["key"])
            self.__setattr__(field["key"], value)

    def get_value(self, msg, entry):
        """get value for entry from keychain if present
           else ask user to supply value (and store it)"""
        value = keyring.get_password(self.namespace, entry)
        if value in (None, ""):
            # noinspection PyTypeChecker
            value = simpledialog.askstring("Input",
                                           msg,
                                           parent=self.gui_root) \
                if self.gui_root else Prompt.ask(msg)
            keyring.set_password(self.namespace, entry, value)
            value = keyring.get_password(self.namespace, entry)
        return value

    def reset_keys(self):
        for field in self.api_fields:
            # noinspection PyUnresolvedReferences
            try:
                keyring.delete_password(self.namespace, field['key'])
            except keyring.errors.PasswordDeleteError:
                logging.info(f"key '{field['key']}' not found in "
                             f"'{self.namespace}' keyring storage")
                pass


# School specific
EDUCATIONS = ('BANL',
              'BAUK',
              'MA',
              'PM_MA',
              'ULO',
              'PM_ULO',
              'MACS',
              'PM_MACS',
              'GV',
              'PM_GV',
              'BIJVAK'
              )

# communities can have multiple educations
COMMUNITY_EDU_IDS = {'banl': ['banl', 'pm_ma', 'pm_ulo', 'pm_gv'],  # nl
                     'bauk': ['bauk', 'pm_macs'],  # uk
                     'macs': ['macs'],
                     'ma': ['ma', 'gv', 'ulo'],
                     'acskills': [edu.lower() for edu in EDUCATIONS]
                     }

# the 'communities-courses' which can have sections
COMMUNITIES = dict(
    acskills=(4485, None),
    theoonline=(4472, None),
    banl=(4221, dict(
          banl=7609,
          pm_ma=117497,
          pm_ulo=117499,
          pm_gv=117498)),
    bauk=(4227, dict(
        bauk=7618,
        pm_macs=117501)),
    macs=(4230, None),
    ma=(4228, dict(
        ma=7619,
        gv=117490,
        ulo=117491))
    )


SHORTNAMES = dict(
    bho1=4285,
    bho2=4440,
    bho3=4441,
    bgo1=10540,
    theol_credo=4472,
    spirsam=7660)

STUDADMIN = ('rsackman',
             'smvries')

now = datetime.now()
# July first is considered the end of educational season
AC_YEAR = now.year - 1 if now.month < 8 else now.year
LAST_YEAR = '-{0}-{1}'.format(AC_YEAR - 1, AC_YEAR)
THIS_YEAR = '-{0}-{1}'.format(AC_YEAR, AC_YEAR + 1)
NEXT_YEAR = '-{0}-{1}'.format(AC_YEAR + 1, AC_YEAR + 2)

EXAMINATION_FOLDER = "Tentamens"


def load_config(default_path='ca_robot.yaml'):
    """
    Setup configuration:
    using yaml config from
    :param default_path:
    """
    path = default_path
    config = None
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
    return config


valid_roles = validators.IS_IN_SET({"T": "Teacher",
                                    "TA": "Teaching Assistant",
                                    "O": "Observer",
                                    "PS": "Proctorio Surveillant",
                                    "S": "Student"})


# noinspection PyCallingNonCallable,PyProtectedMember
class LocalDAL(DAL):
    def __init__(self, is_testing=False, fake_migrate_all=False, folder="databases"):
        url = 'sqlite://testing.sqlite' if is_testing else 'sqlite://storage.sqlite'
        super(LocalDAL, self).__init__(url,
                                       folder=folder,
                                       migrate=True,
                                       migrate_enabled=True,
                                       fake_migrate=False,
                                       fake_migrate_all=fake_migrate_all)

        self.define_table('setting',
                          Field('last_db_update', 'datetime'),
                          singular='Canvasrobot setting',
                          plural='CanvasRobot settings',
                          migrate=False)

        self.define_table('course',
                          Field('course_id', 'integer'),
                          Field('course_code', 'string'),
                          Field('sis_code', 'string'),
                          Field('ac_year', 'string'),
                          Field('name', 'string'),
                          Field('creation_date', 'date'),
                          Field('teachers', 'list:string'),  # as usernames
                          Field('teachers_names', 'list:string'),
                          Field('status', 'integer'),
                          Field('nr_students', 'integer'),
                          Field('nr_modules', 'integer'),
                          Field('nr_module_items', 'integer'),
                          Field('nr_pages', 'integer'),
                          Field('nr_assignments', 'integer'),
                          Field('nr_quizzes', 'integer'),
                          Field('nr_files', 'integer'),
                          # Field('nr_collaborations', 'integer'),
                          Field('nr_ext_urls', 'integer'),
                          Field('assignments_summary', 'string'),
                          Field('examinations_summary', 'string'),
                          Field('examinations_ok', 'boolean', default=False),
                          Field('examinations_findings', 'string'),
                          Field('examinations_details_osiris', 'string'),
                          Field('gradebook', 'upload', uploadfield='gradebook_file'),
                          Field('gradebook_file', 'blob'),
                          singular='LMS course',
                          plural='LMS courses',
                          format='%(name)s[%(teacher_names)s]')

        # To record a controlled set of names referring to examination assignments
        # We override the (sound) pyDAL principle to use course->id as reference
        # because we need the canvas course_id for browser links
        # Note that Pydal create a foreign key to course->id we need to change
        # using DBrowser
        self.define_table('examination',
                          Field('course',
                                'reference course',
                                requires=validators.IS_IN_DB(self, 'id',
                                                             self.course._format)),
                          Field('course_name', 'string'),  # a bit redundant
                          Field('name', 'string'),
                          Field('ignore', 'boolean',
                                label="Skip unused/unusable assignments",
                                default=False),
                          format='%(name)s',
                          singular='Examination name',
                          plural='Examination names')

        self.define_table('user',
                          Field('user_id', 'integer'),
                          Field('username', 'string'),
                          Field('fname', 'string'),
                          Field('first_name', 'string'),
                          Field('prefix', 'string'),
                          Field('last_name', 'string'),
                          Field('email', 'string'),
                          Field('primary_role', 'string', requires=valid_roles),
                          format=('%(first_name)s %(prefix)s '
                                  '%(last_name)s[%(username)s]'),
                          singular='User',
                          plural='Users')

        self.define_table('course2user',
                          Field('course',
                                'reference course',
                                requires=validators.IS_IN_DB(self, 'course.id',
                                                             self.course._format)),
                          Field('user',
                                'reference user',
                                requires=validators.IS_IN_DB(self, 'user.id',
                                                             self.user._format)),
                          Field('role', 'string',
                                requires=valid_roles))

        # self.course.no_students = Field.Virtual(
        #   'no_students',
        #   lambda row: self.((self.course2user.course == row.course.id) &
        #                     (self.course2user.role == 'S')).count())

        self.define_table('submission',
                          Field('submission_id', 'integer'),
                          Field('assigment_id', 'integer'),
                          Field('course_id', 'integer'),
                          Field('user_id', 'integer'),
                          Field('submission_type', 'string'),
                          Field('url', 'string'),
                          Field('grade', 'string'),
                          Field('graded_at', 'string'),
                          format='%(submission_id)s-%(assigment_id)s %(user_id)s',
                          singular='Submission',
                          plural='Submissions')

        self.define_table('document',
                          Field('course',
                                'reference course',
                                requires=validators.IS_IN_DB(self, 'course.id',
                                                             self.course._format)),
                          Field('filename', 'string'),  # from lms
                          Field('content_type', 'string'),  # from lms
                          Field('size', 'integer'),  # from lms
                          Field('folder_id', 'integer'),  # from lms
                          Field('url', 'string'),  # from lms
                          # editor 0= unchecked 1= failed =  2: ok
                          Field('check_status', 'integer', default=0),
                          Field('upload_status', 'integer'),  # upload status lms
                          Field('download_status', 'integer'),  # upload status lms
                          Field('memo', 'string'),  # memo
                          # safe upload of files, keeps filenames
                          Field('file', 'upload'),
                          migrate=True)

        self.define_table('course_urltransform',
                          Field('dryrun','boolean'),
                          Field('course_id', 'integer'),
                          Field('course_code', 'string'),
                          Field('sis_code', 'string'),
                          Field('name', 'string'),
                          Field('teacher_logins', 'list:string'),  # as usernames
                          Field('teacher_names', 'list:string'),
                          Field('status', 'integer'),
                          Field('nr_pages', 'integer'),
                          Field('nr_module_items', 'integer'),
                          Field('nr_assignments', 'integer'),
                          Field('nr_quizzes', 'integer'),
                          Field('nr_files', 'integer'),
                          Field('page_titles', 'list:string'),
                          Field('page_urls', 'list:string'),
                          Field('module_items', 'list:integer'),
                          singular='Course Url transform',
                          plural='Course Url transforms',
                          format='%(name)s[%(teacher_names)s]')

        if is_testing:
            self.truncate_all_tables()

    def truncate_all_tables(self):
        self.commit()
        for table_name in self.tables():
            self[table_name].truncate('RESTART IDENTITY CASCADE')
        self.commit()


global_config = load_config()

if logging and logging.config and global_config:
    logging.config.dictConfig(
        global_config['logging'])  # this created named loggers like 'ca_robot.cli'
