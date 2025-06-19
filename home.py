import plotly.graph_objects as go
import io
import streamlit as st
import pandas as pd
import gspread
from collections import OrderedDict
from google.oauth2.service_account import Credentials
from streamlit_plotly_events import plotly_events

# إعداد صفحة Streamlit
st.set_page_config(layout="wide", page_title="🌳 مشجر أسرة آل دوغان")





# ====== إضافة تسجيل الدخول ======
@st.cache_data
def load_user_data():
    SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(info, scopes=SCOPE)
    client = gspread.authorize(creds)
    SHEET_ID = "1-PCikSMV6dQGnPVgBPkmxsqKv3V0OvoSLKF7JLM9uHQ"
    sheet = client.open_by_key(SHEET_ID).sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

user_data = load_user_data()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    
    
    if st.button("🔁 تحديث البيانات الآن"):
        load_user_data.clear()  # مسح الكاش
        # load_data.clear()     # ← علق هذا السطر إذا ما كنت معرف الدالة
        st.success("✅ تم تحديث البيانات بنجاح! الرجاء إعادة تحميل الصفحة إذا لم تظهر التغييرات.")
        st.stop()

    
    st.title("🔐 تسجيل الدخول")
    with st.form("login_form"):
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        submitted = st.form_submit_button("دخول")
        if submitted:
            if ((user_data['Username'] == username) & (user_data['Password'] == password)).any():
                st.session_state["authenticated"] = True
                st.success("✅ تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
    st.stop()



st.markdown("""
<style>
div[data-testid="stCheckbox"] > label {
    display: flex;
    justify-content: center;
    font-size: 20px !important;
    color: #ff0000 !important;
    font-weight: bold;
    margin: 10px auto;
}
html, body, .main { background-color: #ffffff !important; }
.zoom-container {
    display: flex !important;
    justify-content: center !important;
    gap: 15px !important;
    margin-top: 20px !important;
}
.selected-card {
    padding: 25px;
    border-radius: 18px;
    border: 3px solid #28a745 !important;
    box-shadow: 0 0 15px rgba(40,167,69,0.5);
    margin-top: 10px;
    transition: 0.3s ease;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    SCOPE = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
    info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(info, scopes=SCOPE)
    client = gspread.authorize(creds)
    SHEET_ID = "1h66szakFiAcT2NE3aRzotCABKu_YglFhEchCjzkbwIA"
    sheet = client.open_by_key(SHEET_ID).sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df["order"] = df.index
    df = df.loc[:, ~df.columns.str.match(r'^\d+$')]
    df = df.rename(columns={
        'ID': 'id', 
        'Full Name': 'name', 
        'Sex (M/F)': 'gender',
        'Father ID': 'father_id', 
        'Date of Birth': 'birth', 
        'Date of Death': 'death'
    })
    return df

data = load_data()

# قاموس التعريب
column_translations = {
    'id': 'المعرف',
    'name': 'الاسم الكامل',
    'gender': 'الجنس',
    'father_id': 'معرف الأب',
    'birth': 'تاريخ الميلاد',
    'death': 'تاريخ الوفاة'
}

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="text-align: center; margin-top: 10px;">
        <a href="https://joghaiman.streamlit.app/" target="_blank">
            <img class="responsive-logo" src="https://yemen-saeed.com/user_images/news/10-05-16-677169802.jpg" alt="الصفحة الرئيسية" style="height: 200px;">
        </a>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="text-align: center; margin-top: 20px;">
        <h2 style="color:#222; margin: 0;">🌳 مشجر أسرة آل دوغان</h2>
        <h5 style="color:#444; margin: 0;">عدد الأفراد: {len(data)}</h5>
    </div>
    """, unsafe_allow_html=True)


if 'is_mobile' not in st.session_state:
    st.session_state.is_mobile = False

if 'zoom' not in st.session_state:
    st.session_state.zoom = 1.0

if 'changed_by_mobile_toggle' not in st.session_state:
    st.session_state.changed_by_mobile_toggle = False

previous_is_mobile_state = st.session_state.is_mobile

# إنشاء خانة الاختيار
st.session_state.is_mobile = st.checkbox(
    "📱 هل تستخدم هاتف؟", 
    value=st.session_state.is_mobile, 
    key="mobile_view_checkbox"
)

# إذا تغيرت حالة الجوال
if st.session_state.is_mobile != previous_is_mobile_state:
    st.session_state.changed_by_mobile_toggle = True
    if st.session_state.is_mobile:
        st.session_state.zoom = 1.0
    else:
        st.session_state.zoom = 1.0
    st.rerun()

# بعد الريرن نرجع المتغير False
if st.session_state.changed_by_mobile_toggle:
    st.session_state.changed_by_mobile_toggle = False



opts = []
for _, r in data.iterrows():
    # استخراج اسم الأب من معرف الأب
    father_name = ''
    if pd.notna(r['father_id']):
        father_row = data[data['id'] == r['father_id']]
        if not father_row.empty:
            father_name = father_row.iloc[0]['name']
    
    # استخراج الفخذ من العمود رقم 7 (أي العمود التاسع بما أن الترقيم يبدأ من 0)
    fakhdh = r.iloc[7] if pd.notna(r.iloc[7]) else ''

    # بناء النص بدون الشرطة وبدون كلمة "ابن"
    option_text = f"{r['name']} {father_name} {fakhdh} [{r['id']}]"
    opts.append(option_text)




sel = st.selectbox("👤 اكتب رقم المعرف ثم الاسم", opts, index=0)
tree_type = st.radio(
    "🌳 نوع المشجر",
    ["الأنسال (الأبناء)", "الأسلاف (الآباء)", "الكل (أسلاف + أنسال)"],
    horizontal=True
)
generations = st.slider("📚 عدد الأجيال", 1, 15, 8)


import re

match = re.search(r'\[(\d+)\]$', sel)
if match:
    person_id = int(match.group(1))
else:
    st.error("لم يتم العثور على المعرف في السطر المحدد.")



col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    st.markdown("<h5 style='text-align:right;'>🎀 لون الإناث</h5>", unsafe_allow_html=True)
with col2:
    female_color = st.color_picker("", "#F1ACC8", label_visibility="collapsed")
with col3:
    st.markdown("<h5 style='text-align:right;'>🎩 لون الذكور</h5>", unsafe_allow_html=True)
with col4:
    male_color = st.color_picker("", "#81C3F1", label_visibility="collapsed")





def get_descendants(df, pid, gens):
    t = OrderedDict({0: [pid]})
    for g in range(1, gens + 1):
        if g - 1 not in t:
            break
        cur = []
        for p in t[g - 1]:
            kids = df[df['father_id'] == p]['id'].tolist()
            cur.extend(kids)
        if cur:
            t[g] = cur
    return t

def get_ancestors(df, pid, gens):
    t = {0: [pid]}
    for g in range(1, gens + 1):
        prev = t.get(g - 1, [])
        cur = []
        for c in prev:
            r = df[df['id'] == c]
            if not r.empty:
                f = r['father_id'].iloc[0]
                if pd.notna(f):
                    cur.append(f)
        if cur:
            t[g] = cur
    return t

def merge_trees(a, d):
    # تحوّل مفاتيح شجرة الأسلاف إلى قيم سالبة ثم دمجها مع شجرة الأنسال
    return {**{-k: v for k, v in a.items()}, **d}

def prepare_sunburst(df, tree, center_ancestors=False):
    """
    إذا كان center_ancestors مفعل، نحدد الجذر بناءً على عمق الأسلاف:
      - إذا كانت مفاتيح الشجرة تحتوي على قيم سالبة (نتيجة الدمج)، يكون الجذر عند min(keys).
      - وإذا كانت المفاتيح إيجابية (شجرة الأسلاف فقط) يكون الجذر عند max(keys).
    أما إذا كان غير مفعل (أي في وضع الأنسال) فيكون الشخص المختار هو المحور.
    """
    ids, labels, parents, genders, hov = [], [], [], [], []
    info = df.set_index('id').to_dict('index')
    seen = set()
    if center_ancestors:
        keys = list(tree.keys())
        if keys and min(keys) < 0:
            center_depth = min(keys)
        else:
            center_depth = max(keys)  # بالنسبة لشجرة الأسلاف فقط، نختار الأعمق (أكبر قيمة)
    else:
        center_depth = None

    for depth, nodes in tree.items():
        for n in nodes:
            if n in seen:
                continue
            seen.add(n)
            rec = info.get(n, {})
            nm = rec.get('name', 'غير معروف')
            g = rec.get('gender', 'M')
            b = rec.get('birth', '')
            dth = rec.get('death', '')
            by = pd.to_datetime(b, errors='coerce').year if b else ''
            dy = pd.to_datetime(dth, errors='coerce').year if dth else ''
            name_id = f"<b>{nm}</b><br><span style='color:blue'>{n}</span>"
            date_line = (
                f"<span style='color:green'>{by}</span> - <span style='color:red'>{dy}</span>"
                if by and dy else f"<span style='color:green'>{by}</span>" if by else f"<span style='color:red'>{dy}</span>"
            )
            label_text = f"{name_id}<br>{date_line}" if date_line else name_id
            labels.append(label_text)
            ids.append(str(n))
            genders.append(g)
            # شرط التحديد:
            # - إذا كان center_ancestors مفعل، نطابق العمق مع center_depth.
            # - أما إذا كان غير مفعل (وضع الأنسال) فيجب أن تكون العقدة التي تساوي person_id هي المركز.
            if (center_ancestors and center_depth is not None and depth == center_depth) or (not center_ancestors and n == person_id):
                parents.append('')
            else:
                fpid = rec.get('father_id', '')
                parents.append(str(int(fpid)) if pd.notna(fpid) and fpid != '' else '')
            hover_lines = [
    f"<span style='color:#800000;font-weight:bold;font-size:16px;'>المعرف:</span> "
    f"<span style='color:darkblue;font-weight:bold;font-size:14px;'>{n}</span>"
]




            for col in df.columns:
                if col in ['id', 'order', 'صورة']:
                    continue
                translated_col = column_translations.get(col, col)
                value = rec.get(col, '')
                if pd.isna(value) or str(value).strip() == '':
                    continue
                if col == 'gender':
                    value = 'ذكر' if value == 'M' else 'أنثى'
                if col == 'father_id':
                    try:
                        father_name = df[df['id'] == int(value)]['name'].values[0]
                        value = f"{father_name} ({value})"
                    except:
                        value = f"({value})"
                hover_lines.append(
    f"<span style='color:#800000;font-weight:bold;font-size:16px;'>{translated_col}:</span> "
    f"<span style='color:darkblue;font-weight:bold;font-size:14px;'>{value}</span>"
)

            hov.append("<br>".join(hover_lines))
    return ids, labels, parents, genders, hov

def draw(df, tree, mcol, fcol, zoom, center_ancestors=False):
    ids, labels, parents, genders, hov = prepare_sunburst(df, tree, center_ancestors=center_ancestors)
    cols = [mcol if g == 'M' else fcol for g in genders]
    
# الأسطر الجديدة التي ستضيفها لحساب حجم الخط sz:
    # الحصول على إعدادات حجم الخط الأساسي والتكبير الحالي
    # افترض أن font_size قد يكون لديك كإعداد إضافي للمستخدم، وإلا سيعتمد على 18
    base_font_size = st.session_state.get("font_size", 18) 
    current_zoom_level = zoom  # 'zoom' هو معامل يتم تمريره للدالة draw

    # التحقق إذا كان وضع الهاتف مفعل من خلال متغيرات الحالة
    if st.session_state.get("is_mobile", False):
        # إذا كان وضع الهاتف، طبق حجم خط أصغر ومدى أضيق
        # مثال: تصغير إضافي بنسبة وجعل الحدود (الأصغر والأكبر) أقل
        sz = min(16, max(8, int(base_font_size * current_zoom_level * 0.8))) 
    else:
        # إذا لم يكن وضع الهاتف، استخدم الحساب الأصلي لحجم الخط
        sz = min(26, max(10, int(base_font_size * current_zoom_level)))

    fig = go.Figure(go.Sunburst(
        ids=ids,
        labels=labels,
        parents=parents,
        sort=False,
        marker=dict(colors=cols),
        branchvalues='total',
        hovertext=hov,
        hoverinfo='text',
        insidetextorientation='auto',
        textinfo='label',
        textfont=dict(size=sz)
    ))
    
    fig.update_layout(
    margin=dict(t=10, l=10, r=10, b=10),
    autosize=True,
    height=700,
    hoverlabel=dict(bgcolor="white", font_size=14, font_family="Cairo", align="right", namelength=-1)
)


    return fig

# تحديد نمط الرسم بناءً على نوع الشجرة:
if tree_type == "الأنسال (الأبناء)":
    t = get_descendants(data, person_id, generations)
    center_mode = False  # في وضع الأنسال يكون الشخص المختار هو المركز
elif tree_type == "الأسلاف (الآباء)":
    t = get_ancestors(data, person_id, generations)
    center_mode = True   # في وضع الأسلاف يكون السلف الأبعد هو المركز
else:
    t = merge_trees(get_ancestors(data, person_id, generations), get_descendants(data, person_id, generations))
    center_mode = True   # عند الدمج، نفضل أن يكون الجزء الأسلافي هو المحور

# --- عرض بطاقة الأب والأبناء في نفس السطر أو الأب فقط إن لم يكن لديه أبناء ---


# --- عرض بطاقة الأب والأبناء في نفس السطر أو الأب فقط إن لم يكن لديه أبناء ---

# استخراج بيانات الأب
person_row = data[data['id'] == person_id].iloc[0]
صورة_الأب  = person_row.get('صورة', '').replace("uc?export=view", "thumbnail")
اسم_الأب   = person_row['name']

# استخراج الأبناء وتصنيفهم
أبناء       = data[data['father_id'] == person_id]
أبناء_إناث  = أبناء[أبناء['gender'].str.strip().str.upper() == 'F']
أبناء_ذكور  = أبناء[أبناء['gender'].str.strip().str.upper() == 'M']

# HTML للبنات (65×65px) مع عكس الترتيب
left_html = "".join([
    f'<div style="text-align:center;">'
    f'<img src="{row.get("صورة","").replace("uc?export=view","thumbnail")}" '
       f'width="65" height="65" style="border-radius:50%;object-fit:cover;">'
    f'<p style="margin:0;color:#e83e8c;font-weight:bold;">{row["name"]}</p>'
    f'</div>'
    for _, row in أبناء_إناث.iloc[::-1].iterrows()  # نعيك الصفوف هنا
])


# HTML للأب (100×100px)
center_html = (
    f'<div style="text-align:center;">'
    f'<img src="{صورة_الأب}" width="100" height="100" style="border-radius:50%;object-fit:cover;">'
    f'<h3 style="margin:0;color:#000;font-weight:bold;">{اسم_الأب}</h3>'
    f'</div>'
)

# HTML للأبناء (75×75px)
right_html = "".join([
    f'<div style="text-align:center;">'
    f'<img src="{row.get("صورة","").replace("uc?export=view","thumbnail")}" '
       f'width="75" height="75" style="border-radius:50%;object-fit:cover;">'
    f'<p style="margin:0;color:#007bff;font-weight:bold;">{row["name"]}</p>'
    f'</div>'
    for _, row in أبناء_ذكور.iterrows()
])

# حاوية رابعة فارغة
placeholder_html = ""

# نضمّن media query كما كان سابقاً (عند أكثر من طفل واحد)
num_kids = len(أبناء_إناث) + len(أبناء_ذكور)
style_block = ""
if num_kids > 1:
    style_block = """
    <style>
    @media (max-width: 768px) {
      .parent-container { flex-direction: column !important; }
      .parent-container > div:nth-child(2) { order: 1; }
      .parent-container > div:nth-child(3) { order: 2; }
      .parent-container > div:nth-child(1) { order: 3; }

      .parent-container > div:nth-child(2) img {
          width: 75px !important; height: 75px !important;
      }
      .parent-container > div:nth-child(1) img {
          width: 40px !important; height: 40px !important;
      }
      .parent-container > div:nth-child(3) img {
          width: 45px !important; height: 45px !important;
      }

      .parent-container p {
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          max-width: 70px;
          margin: 0;
      }
    }
    </style>
    """

# نجمع الأربع حاويات مع الحفاظ على الأحجام الأصلية
html_card = f"""
{style_block}
<div class="parent-container" style="
     display: flex;
     justify-content: center;
     align-items: center;
     gap: 30px;
     margin: 0 auto;
     padding: 15px;
     max-width: 1000px;
     background-color: transparent;
">
  <!-- 1) بنات -->
  <div style="display: flex; flex-direction: row; align-items: center; gap: 10px;">
    {left_html}
  </div>
  <!-- 2) الأب -->
  {center_html}
  <!-- 3) أبناء -->
  <div style="display: flex; flex-direction: row; align-items: center; gap: 10px;">
    {right_html}
  </div>
  <!-- 4) حاوية رابعة -->
  <div style="display: flex; flex-direction: row; align-items: center; gap: 10px;">
    {placeholder_html}
  </div>
</div>
"""

# عرض البطاقة في Streamlit
st.markdown(html_card, unsafe_allow_html=True)





# --- عرض المخطط في المنتصف ---
fig = draw(data, t, male_color, female_color, st.session_state['zoom'], center_ancestors=center_mode)

st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True, key="sunburst_chart")
st.markdown("</div>", unsafe_allow_html=True)



st.markdown("<div class='zoom-container'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("➖ تصغير", key="zoom_out"):
        st.session_state.zoom = max(st.session_state.zoom - 0.1, 0.2)
        st.session_state.changed_by_mobile_toggle = False
        st.rerun()
with col2:
    st.markdown(f"<div style='text-align:center;font-weight:bold;margin-top:8px;'>🔍 {st.session_state.zoom * 100:.0f}%</div>", unsafe_allow_html=True)
with col3:
    if st.button("➕ تكبير", key="zoom_in"):
        st.session_state.zoom = min(st.session_state.zoom + 0.1, 3.0)
        st.session_state.changed_by_mobile_toggle = False
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
