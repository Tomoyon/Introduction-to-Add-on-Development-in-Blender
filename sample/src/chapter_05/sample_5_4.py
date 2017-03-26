import bpy
from bpy.props import BoolProperty, IntProperty
from bpy.props import PointerProperty, IntVectorProperty
from bpy_extras import view3d_utils
from mathutils import Vector
import blf


bl_info = {
    "name": "サンプル5-4: オブジェクト名の表示サポート",
    "author": "Nutti",
    "version": (2, 0),
    "blender": (2, 75, 0),
    "location": "3Dビュー > プロパティパネル > オブジェクト名の表示サポート",
    "description": """オブジェクトの位置にオブジェクト名を表示し、マウスカーソルの位置に
                      向けて発したレイと交差するオブジェクト名を表示するアドオン""",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"
}


# プロパティ
class SON_Properties(bpy.types.PropertyGroup):

    running = BoolProperty(
        name="動作中",
        description="オブジェクト名の表示サポート機能が動作中か？",
        default=False
    )


# オブジェクト名を表示
class ShowObjectName(bpy.types.Operator):

    bl_idname = "view3d.show_object_name"
    bl_label = "オブジェクト名の表示サポート"
    bl_description = """オブジェクトの位置にオブジェクト名を表示し、マウスカーソルの位置に
                        向けて発したレイと交差するオブジェクト名を表示します"""

    __handle = None           # 描画関数ハンドラ

    def __init__(self):
        self.__intersected_objs = []      # マウスカーソルの位置に向けて発したレイと交差するオブジェクト一覧

    def __handle_add(self, context):
        if ShowObjectName.__handle is None:
            # 描画関数の登録
            ShowObjectName.__handle = bpy.types.SpaceView3D.draw_handler_add(
                ShowObjectName.__render, (self, context),
                'WINDOW', 'POST_PIXEL'
            )
            # モーダルモードへの移行
            context.window_manager.modal_handler_add(self)

    def __handle_remove(self, context):
        if ShowObjectName.__handle is not None:
            # 描画関数の登録を解除
            bpy.types.SpaceView3D.draw_handler_remove(
                ShowObjectName.__handle, 'WINDOW'
            )
            ShowObjectName.__handle = None

    @staticmethod
    def __render_message(size, x, y, msg):
        blf.size(0, size, 72)
        blf.position(0, x, y, 0)
        blf.draw(0, msg)

    @staticmethod
    def __get_region_space(context, area_type, region_type, space_type):
        region = None
        area = None
        space = None

        # 指定されたエリアを取得する
        for a in context.screen.areas:
            if a.type == area_type:
                area = a
                break
        else:
            return (None, None)
        # 指定されたリージョンを取得する
        for r in area.regions:
            if r.type == region_type:
                region = r
                break
        # 指定されたスペースを取得する
        for s in area.spaces:
            if s.type == space_type:
                space = s
                break

        return (region, space)

    @staticmethod
    def __render(self, context):
        prefs = context.user_preferences.addons[__name__].preferences

        region, space = ShowObjectName.__get_region_space(
            context, 'VIEW_3D', 'WINDOW', 'VIEW_3D'
        )
        if (region is None) or (space is None):
            return

        # オブジェクトの位置にオブジェクト名を表示
        objs = [o for o in bpy.data.objects]
        # オブジェクトの位置座標（3D座標）をリージョン座標（2D座標）に変換
        locs_on_screen = [
            view3d_utils.location_3d_to_region_2d(
                region,
                space.region_3d,
                o.location
            ) for o in objs
        ]
        blf.shadow(0, 3, 0.1, 0.1, 0.1, 1.0)
        blf.shadow_offset(0, 1, -1)
        blf.enable(0, blf.SHADOW)
        for obj, loc in zip(objs, locs_on_screen):
            # 表示範囲外なら表示しない
            if loc is not None:
                ShowObjectName.__render_message(
                    prefs.font_size_2, loc.x, loc.y, obj.name
                )
        blf.disable(0, blf.SHADOW)

        # マウスカーソルの位置に向けて発したレイと交差するオブジェクト名を表示
        blf.shadow(0, 3, 0.0, 1.0, 0.0, 0.5)
        blf.shadow_offset(0, 2, -2)
        blf.enable(0, blf.SHADOW)
        ShowObjectName.__render_message(
            prefs.font_size_1,
            prefs.left_top[0],
            region.height - prefs.left_top[1],
            "Intersect"
        )
        blf.disable(0, blf.SHADOW)
        # ray_castが可能なオブジェクトモード時のみ表示
        if context.mode == 'OBJECT':
            for i, o in enumerate(self.__intersected_objs):
                ShowObjectName.__render_message(
                    int(prefs.font_size_1 * 0.8),
                    prefs.left_top[0],
                    (region.height - prefs.left_top[1]
                     - int(prefs.font_size_1 * 1.3)
                     - i * int(prefs.font_size_1 * 0.9)),
                    o.name
                )
        else:
            ShowObjectName.__render_message(
                int(prefs.font_size_1 * 0.8),
                prefs.left_top[0],
                (region.height - prefs.left_top[1]
                 - int(prefs.font_size_1 * 1.3)),
                "Objectモード以外では利用できません"
            )

    def modal(self, context, event):
        props = context.scene.son_props

        if context.mode == 'OBJECT':
            # マウスカーソルのリージョン座標を取得
            mv = Vector((event.mouse_region_x, event.mouse_region_y))
            # 3Dビューエリアのウィンドウリージョンと、スペースを取得する
            region, space = ShowObjectName.__get_region_space(
                context, 'VIEW_3D', 'WINDOW', 'VIEW_3D'
            )
            # マウスカーソルの位置に向けて発したレイの方向を求める
            ray_dir = view3d_utils.region_2d_to_vector_3d(
                region,
                space.region_3d,
                mv
            )
            # マウスカーソルの位置に向けて発したレイの発生源を求める
            ray_orig = view3d_utils.region_2d_to_origin_3d(
                region,
                space.region_3d,
                mv
            )
            # レイの始点
            start = ray_orig
            # レイの終点（線分の長さは2000とした）
            end = ray_orig + ray_dir * 2000
            # カメラやライトなど、メッシュ型ではないオブジェクトは除く
            objs = [o for o in bpy.data.objects if o.type == 'MESH']
            self.__intersected_objs = []
            for o in objs:
                try:
                    # レイとオブジェクトの交差判定
                    mwi = o.matrix_world.inverted()
                    result = o.ray_cast(mwi * start, mwi * end)
                    # オブジェクトとレイが交差した場合は交差した面のインデックス、交差しない場合は-1が返ってくる
                    if result[2] != -1:
                        self.__intersected_objs.append(o)
                # メッシュタイプのオブジェクトが作られているが、ray_cast対象の面が存在しない場合
                except RuntimeError:
                    print("""サンプル5-4: オブジェクト生成タイミングの問題により、
                             例外エラー「レイキャスト可能なデータなし」が発生""")

        # 3Dビューの画面を更新
        if context.area:
            context.area.tag_redraw()

        # 作業時間計測を停止
        if props.running is False:
            self.__handle_remove(context)
            return {'FINISHED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        props = context.scene.son_props
        if context.area.type == 'VIEW_3D':
            # 開始ボタンが押された時の処理
            if props.running is False:
                props.running = True
                self.__handle_add(context)
                print("サンプル5-4: オブジェクト名の表示を開始しました。")
                return {'RUNNING_MODAL'}
            # 終了ボタンが押された時の処理
            else:
                props.running = False
                print("サンプル5-4: オブジェクト名の表示を終了しました。")
                return {'FINISHED'}
        else:
            return {'CANCELLED'}


# UI
class OBJECT_PT_SON(bpy.types.Panel):

    bl_label = "オブジェクト名の表示サポート"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        sc = context.scene
        layout = self.layout
        props = sc.son_props
        # 開始/停止ボタンを追加
        if props.running is False:
            layout.operator(ShowObjectName.bl_idname, text="開始", icon="PLAY")
        else:
            layout.operator(ShowObjectName.bl_idname, text="終了", icon="PAUSE")


# ユーザー・プリファレンスのアドオン設定情報
class SON_Preferences(bpy.types.AddonPreferences):

    bl_idname = __name__

    # 交差したオブジェクトの名前表示に使用する設定
    font_size_1 = IntProperty(
        name="Font Size",
        description="フォントサイズ",
        default=20,
        max=50,
        min=10
    )
    left_top = IntVectorProperty(
        name="左上座標",
        description="情報を表示する左上の座標",
        size=2,
        subtype='XYZ',
        default=(20, 60),
        max=300,
        min=0
    )
    # オブジェクトの位置に表示する時に使用する設定
    font_size_2 = IntProperty(
        name="Font Size",
        description="フォントサイズ",
        default=12,
        max=50,
        min=10
    )

    def draw(self, context):
        layout = self.layout

        layout.label("UI: ")
        sp = layout.split(percentage=0.5)
        col = sp.column()
        col.label("交差したオブジェクト名の表示: ")
        col.prop(self, "left_top")
        col.prop(self, "font_size_1")
        sp = layout.split(percentage=0.5)
        col = sp.column()
        col.label("オブジェクトの位置にオブジェクト名を表示: ")
        col.prop(self, "font_size_2")


# プロパティの作成
def init_props():
    sc = bpy.types.Scene
    sc.son_props = PointerProperty(
        name="プロパティ",
        description="本アドオンで利用するプロパティ一覧",
        type=SON_Properties)


# プロパティの削除
def clear_props():
    sc = bpy.types.Scene
    del sc.son_props


def register():
    bpy.utils.register_module(__name__)
    init_props()
    print("サンプル5-4: アドオン「サンプル5-4」が有効化されました。")


def unregister():
    clear_props()
    bpy.utils.unregister_module(__name__)
    print("サンプル5-4: アドオン「サンプル5-4」が無効化されました。")


if __name__ == "__main__":
    register()
