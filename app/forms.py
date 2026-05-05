from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField

class EmployeeSearchForm(FlaskForm):
    keyword = StringField("検索")

    role = SelectField(
        "権限",
        choices=[
            ("", "すべて"),
            ("admin", "管理者"),
            ("manager", "マネージャー"),
            ("staff", "一般スタッフ"),
        ],
        default=""
    )

    department = SelectField(
        "担当領域",
        choices=[
            ("", "すべて"),
            ("kitchen", "キッチン"),
            ("hall", "ホール"),
            ("all", "全体"),
        ],
        default=""
    )

    submit = SubmitField("検索")

class AuditLogSearchForm(FlaskForm):
    action = SelectField(
        "アクション",
        choices=[
            ("", "すべて"),
            ("create_employee", "登録"),
            ("update_employee", "更新"),
            ("disable_employee", "無効化"),
            ("reset_password", "仮パスワード再発行"),
        ],
        default=""
    )

    keyword = StringField("キーワード")

    submit = SubmitField("検索")
