from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Optional, DataRequired, Length, EqualTo

#従業員検索フォームのWTF化
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

#監査ログ画面の検索フォームとフィルターのWTF化
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

#従業員登録フォームのWTF化
class EmployeeCreateForm(FlaskForm):
    full_name = StringField("氏名", validators=[DataRequired()])
    email = StringField("メールアドレス", validators=[DataRequired(), Email()])
    gender = SelectField(
        "性別",
        choices=[
            ("", "選択してください"),
            ("man", "男性"),
            ("woman", "女性"),
            ("other", "その他"),
        ],
        validators=[Optional()]
    )
    birth_date = DateField("生年月日", validators=[Optional()])
    home_address = StringField("住所", validators=[Optional()])
    store_code = StringField("店番号", validators=[Optional()])
    department = SelectField(
        "担当領域",
        choices=[
            ("", "選択してください"),
            ("kitchen", "キッチン"),
            ("hall", "ホール"),
            ("all", "全体"),
        ],
        validators=[Optional()]
    )
    position = SelectField(
        "役職",
        choices=[
            ("", "選択してください"),
            ("staff", "一般スタッフ"),
            ("store_manager", "店長"),
            ("assistant_manager", "副店長"),
            ("head_chef", "料理長"),
            ("sous_chef", "副料理長"),
        ],
        validators=[Optional()]
    )
    phone_number = StringField("電話番号", validators=[Optional()])
    employment_type = SelectField(
        "雇用区分",
        choices=[
            ("", "選択してください"),
            ("full_time", "正社員"),
            ("contract", "契約社員"),
            ("part_time", "アルバイト/パート"),
            ("temporary", "派遣"),
        ],
        validators=[Optional()]
    )
    hire_date = DateField("入社日", validators=[Optional()])
    role = SelectField(
        "権限",
        choices=[
            ("staff", "一般スタッフ"),
            ("manager", "管理者クラス"),
            ("admin", "本社管理者"),
        ],
        default="staff"
    )
    submit = SubmitField("登録")

#従業員情報の更新フォームのWTF化
class EmployeeEditForm(EmployeeCreateForm):
    submit = SubmitField("更新")

#ログインフォームWTF化
class LoginForm(FlaskForm):
    employee_id = StringField("社員番号", validators=[DataRequired()])
    password = PasswordField("パスワード", validators=[DataRequired()])
    submit = SubmitField("ログイン")

#パスワード変更フォームWTF化
class ChangePasswordForm(FlaskForm):
    new_password = PasswordField(
        "新しいパスワード",
        validators=[
            DataRequired(),
            Length(min=8, message="パスワードは8文字以上で入力してください")
        ]
    )

    confirm_password = PasswordField(
        "確認用パスワード",
        validators=[
            DataRequired(),
            EqualTo("new_password", message="パスワードが一致しません")
        ]
    )

    submit = SubmitField("変更")