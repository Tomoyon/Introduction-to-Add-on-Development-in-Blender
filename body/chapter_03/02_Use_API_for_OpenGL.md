<div id="sect_title_img_3_2"></div>

<div id="sect_title_text"></div>

# OpenGL向けのAPIを利用する

<div id="preface"></div>

###### これまでは、ボタンやメニューなどのBlenderの決まったフレームワークの中でUIを構築する方法を紹介しました。しかし、アドオンの機能によっては独自のUIを構築する必要がある場合もあると思います。独自のUIを構築する方法として、例えばOpenGLを利用する方法が考えられます。本節ではBlenderが提供しているOpenGL向けのAPIを利用し、 *3Dビュー* 上に図形を表示するサンプルを紹介します。

## OpenGLとは？

2D/3D向けのグラフィックAPIは **OpenGL (Open Graphic Library)** と **DirectX** の2つが主流です。
3DCGに何かしら関わっている方はご存知かもしれませんが、それぞれどのような違いがあるのかわからない方のために、OpenGLとDirectXの違いを以下にまとめました。

|　|OpenGL|DirectX|
|---|---|---|
|開発元|Microsoft|シリコングラフィクス|
|主な用途|ゲームの描画|3DCGソフト、CADソフト|
|レンダリング精度|OpenGLに比べて低精度|精度が求められるCADソフトで利用されるため高精度|
|レンダリング速度|高い応答性が求められるゲームで利用されるため高速|DirectXに比べて低速|
|動作環境|Windows, XBox|Windows, Mac, Linux, iOS, Android, Webアプリなど|

上記の比較からもわかるように、3DCGソフトかつ複数のOSでの動作をサポートするBlenderはグラフィックスAPIとしてOpenGLを利用しています。
そしてBlenderは、PythonからOpenGLへアクセスできるようにAPIも用意しているため、ユーザはPythonスクリプトからOpenGLの機能の一部を扱うことができます。

## 作成するアドオンの仕様

* *3Dビュー* エリアに図形を表示
* 表示する図形は、 *プロパティパネル* から選択

## アドオンを作成する

以下のソースコードを、 [1-4節](../chapter_01/04_Install_own_Add-on.md) を参考にして *テキスト・エディタ* に入力し、```sample_8.py``` という名前で保存してください。

[import](../../sample/src/chapter_03/sample_8.py)

## アドオンを実行する

### アドオンを有効化する

[1-4節](../chapter_01/04_Install_own_Add-on.md) を参考に、作成したアドオンを有効化すると *コンソール* に以下の文字列が出力されます。

```sh
サンプル 8: アドオン「サンプル8」が有効化されました。
```

アドオンを有効化すると、 *3Dビュー* エリアの *プロパティパネル* に開始ボタンが表示されます。

![図の表示 手順1](https://dl.dropboxusercontent.com/s/uf0xneikowb5ozz/use_addon_1.png "図の表示 手順1")


### アドオンを使ってみる

以下の手順に従って、作成したアドオンの機能を使ってみます。

<div id="process_title"></div>

##### Work

<div id="process"></div>

|1|開始ボタンをクリックすると、 *3Dビュー* エリア上に三角形が表示されます。<br>また *プロパティパネル* には、表示する図形と図形の頂点を変更するためのUIが表示されます。|![図の表示 手順2](https://dl.dropboxusercontent.com/s/056sg7b9x96mdjf/use_addon_2.png "図の表示 手順2")|
|---|---|---|

<div id="process_sep"></div>

---

<div id="process"></div>

|2|三角形の頂点座標を変更します。*3Dビュー* エリア 上に表示されている三角形が頂点の変更に合わせて変形します。|![図の表示 手順3](https://dl.dropboxusercontent.com/s/vlua7b5aiptcc4m/use_addon_3.png "図の表示 手順3")|
|---|---|---|

<div id="process_sep"></div>

---

<div id="process"></div>

|3|表示する図形を三角形から四角形へ変更します。<br>表示する図形を四角形へ変更すると4つの頂点を編集できるようになり、変更と同時に *3Dビュー* エリア 上に表示されている図形も変更されます。|![図の表示 手順4](https://dl.dropboxusercontent.com/s/1wr0l6uddp64emk/use_addon_4.png "図の表示 手順4")|
|---|---|---|

<div id="process_start_end"></div>

---


### アドオンを無効化する

[1.4節](../chapter_01/04_Install_own_Add-on.md)を参考に、有効化したアドオンを無効化すると *コンソール* に以下の文字列が出力されます。

```sh
サンプル 8: アドオン「サンプル 8」が無効化されました。
```

## ソースコードの解説

### OpenGLへアクセスするためのAPIを利用する

今回のサンプルでは図形を描画するために、Blenderが提供するOpenGLへアクセスするためのAPIを利用します。
OpenGLへアクセスするAPIをアドオンから利用するためには、 ```bgl``` モジュールをインポートする必要があります。

```python
import bgl
```

### アドオンで利用するプロパティを定義する

[3.1節](01_Sample_7_Delete_face_by_mouse_click.md)で紹介したサンプルと同様、今回もクラス間で以下のようなデータを共有します。

|変数|意味|
|---|---|
|```rf_running```|実行中の場合は ```True```|
|```rf_figure```|表示する図形（三角形、四角形）|
|```rf_vert_1```|頂点1の座標（2次元）|
|```rf_vert_2```|頂点2の座標（2次元）|
|```rf_vert_3```|頂点3の座標（2次元）|
|```rf_vert_4```|頂点4の座標（2次元）、四角形表示時のみに利用|

以下のようにして、上記プロパティを追加します。

```python
sc = bpy.types.Scene
sc.rf_running = BoolProperty(
    name = "実行中",
    description = "実行中か？",
    default = False
)
sc.rf_figure = EnumProperty(
    name = "図形",
    description = "表示する図形",
    items = [
        ('TRIANGLE', "三角形", "三角形を表示します"),
        ('RECTANGLE', "四角形", "四角形を表示します")]
)
sc.rf_vert_1 = FloatVectorProperty(
    name = "頂点1",
    description = "図形の頂点",
    size = 2,
    default = (50.0, 50.0)
)
sc.rf_vert_2 = FloatVectorProperty(
    name = "頂点2",
    description = "図形の頂点",
    size = 2,
    default = (50.0, 100.0)
)
sc.rf_vert_3 = FloatVectorProperty(
    name = "頂点3",
    description = "図形の頂点",
    size = 2,
    default = (100.0, 100.0)
)
sc.rf_vert_4 = FloatVectorProperty(
    name = "頂点4",
    description = "図形の頂点",
    size = 2,
    default = (100.0, 50.0)
)
```

定義したプロパティは、アドオン無効化時に削除するようにします。

```python
sc = bpy.types.Scene
del sc.rf_running
del sc.rf_figure
del sc.rf_vert_1
del sc.rf_vert_2
del sc.rf_vert_3
del sc.rf_vert_4
```

### 図形を描画する関数を登録する

*3Dビュー* エリア上で図形を描画する関数を登録するための静的メソッド ```RenderFigure.handle_add()``` を作成します。
```RenderFigure.handle_add()``` は静的メソッドとして作成する必要があるため、デコレータ ```@staticmethod``` をメソッド定義の前につけます。

```python
# 画像描画関数を登録
@staticmethod
def handle_add(self, context):
    if RenderFigure.__handle is None:
        RenderFigure.__handle = bpy.types.SpaceView3D.draw_handler_add(
            RenderFigure.render,
            (self, context), 'WINDOW', 'POST_PIXEL')
```

描画関数の登録は ```bpy.types.SpaceView3D.draw_handler_add()``` 関数で行います。
この関数は、 *3Dビュー* エリア上で描画するための関数を登録します。
ここで ```SpaceView3D``` は *3Dビュー* を指していますが、描画するエリアにより変わります。
関数の引数に指定する値は以下の通りです。

|引数|意味|
|---|---|
|第1引数|描画関数（描画関数は静的メソッド、または通常の関数）|
|第2引数|描画関数に渡す引数リスト|
|第3引数|描画する *リージョン*|
|第4引数|描画モード（深度バッファの扱いを指定、基本は ```POST_PIXEL```）|

今回のサンプルでは、第1引数に ```RenderFigure.render``` 、第3引数に ```WINDOW``` を指定しています。
描画関数に渡す引数は、自身のクラスインスタンスと実行時コンテキストを渡しています。

なお、 ```bpy.types.SpaceView3D.draw_handler_add()```  は戻り値としてハンドルを返します。
ハンドルは、描画関数の登録解除時に利用するため変数に保存しておきます。

### 図形を描画する関数を作成する

図形を描画する静的メソッド ```RenderFigure.render``` を作成します。

```python
@staticmethod
def render(self, context):
    sc = context.scene

    # OpenGLの設定
    bgl.glEnable(bgl.GL_BLEND)

    # 図形を表示
    if sc.rf_figure == 'TRIANGLE':
        bgl.glBegin(bgl.GL_TRIANGLES)
        bgl.glColor4f(1.0, 1.0, 1.0, 0.7)
        bgl.glVertex2f(sc.rf_vert_1[0], sc.rf_vert_1[1])
        bgl.glVertex2f(sc.rf_vert_2[0], sc.rf_vert_2[1])
        bgl.glVertex2f(sc.rf_vert_3[0], sc.rf_vert_3[1])
        bgl.glEnd()
    elif sc.rf_figure == 'RECTANGLE':
        bgl.glBegin(bgl.GL_QUADS)
        bgl.glColor4f(1.0, 1.0, 1.0, 0.7)
        bgl.glVertex2f(sc.rf_vert_1[0], sc.rf_vert_1[1])
        bgl.glVertex2f(sc.rf_vert_2[0], sc.rf_vert_2[1])
        bgl.glVertex2f(sc.rf_vert_3[0], sc.rf_vert_3[1])
        bgl.glVertex2f(sc.rf_vert_4[0], sc.rf_vert_4[1])
        bgl.glEnd()
```

プロパティを取得した後は、基本的にOpenGLを用いた描画手順に従うことで図形を表示します。

最初にOpenGLの設定として、 ```bgl.glEnable(bgl.GL_BLEND)``` により半透明処理を有効化します。
この処理がないと図形描画時に透過が無効になり、期待した結果になりません。

続いて表示する図形の判定を行った後、 ```bgl.glBegin()``` 関数により図形描画を開始します。
引数には描画モードを指定します。
```bgl.GL_TRIANGLES``` を指定することで三角形を、 ```bgl.GL_QUADS``` を指定することで四角形の描画を開始します。

次に ```bgl.glColor4f()``` 関数により図形の色を指定しています。
引数は順に、赤(R)、緑(G)、青(B)、アルファ値(A)となります。
今回はやや半透明の白色の設定にしました。

最後に ```bgl.glVertex2f()``` 関数を呼んで図形の頂点を設定した後に、 ```bgl.glEnd()``` 関数により描画を完了します。
```bgl.glVertex2f()``` 関数の引数には、X座標、Y座標の順で浮動小数点値で指定します。
三角形の場合は3つの頂点を指定すればよいため3回 ```bgl.glVertex2f()``` を呼び、四角形の場合は4つの頂点を指定するため4回 ```bgl.glVertex2f()``` を呼びます。

### 図形を描画する関数を登録解除する

登録した図形を描画する関数はアドオン無効化時に登録解除する必要があります。

```python
@staticmethod
def handle_remove(self, context):
    if RenderFigure.__handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(
            RenderFigure.__handle, 'WINDOW')
        RenderFigure.__handle = None
```

描画関数の登録解除は、 ```bpy.types.SpaceView3D.draw_handler_remove()``` 関数で行います。
描画関数の登録時に使用した ```bpy.types.SpaceView3D.draw_handler_add()``` 関数と同様、 ```SpaceView3D``` は描画関数を登録解除する *エリア* により変わります。
関数の引数は以下の通りです。

|引数|意味|
|---|---|
|第1引数|ハンドル（```draw_handler_add()``` の戻り値）|
|第2引数|描画する *リージョン*|

### UIを構築する

最後に本アドオンのUIを構築します。

```python
class OBJECT_PT_RF(bpy.types.Panel):
    bl_label = "図形を表示"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        sc = context.scene
        layout = self.layout
        if context.area:
            context.area.tag_redraw()
        if sc.rf_running is True:
            layout.operator(RenderingButton.bl_idname, text="Stop", icon="PAUSE")
            layout.prop(sc, "rf_figure", "図形")
            layout.prop(sc, "rf_vert_1", "頂点1")
            layout.prop(sc, "rf_vert_2", "頂点2")
            layout.prop(sc, "rf_vert_3", "頂点3")
            if sc.rf_figure == 'RECTANGLE':
                layout.prop(sc, "rf_vert_4", "頂点4")
        elif sc.rf_running is False:
            layout.operator(RenderingButton.bl_idname, text="Start", icon="PLAY")
```

[3.1節](01_Sample_7_Delete_face_by_mouse_click.md)と同様、 ```bpy.types.Panel``` を継承したクラスの中でUIを構築していきます。

最初に描画中か否かの判定を行った後、描画中であればStopボタンを、そうでない場合はStartボタンを配置しています。
また、描画中であれば描画する図形や頂点の座標を指定できるようにするため、 ```layout.prop()``` 関数を用いてこれらのUIパーツを配置しています。
```layout.prop()``` の引数を以下に示します。

|引数|意味|
|---|---|
|第1引数|プロパティを持つオブジェクト|
|第2引数|プロパティ変数名|
|第3引数|表示文字列|

今回は ```bpy.types.Scene``` にプロパティを登録しているため、 ```context.scene``` を第1引数にしています。
第2引数には、 ```bpy.types.Scene``` に登録したプロパティ変数名を文字列で指定しています。

四角形を描画する場合は4つの頂点を指定可能とするため、描画する図形が四角形である場合に4つ目の頂点を指定するUIパーツを配置するようにします。

最後に、描画開始/終了を行う *オペレーション用クラス* を作成します。

```python
class RenderingButton(bpy.types.Operator):
    bl_idname = "view3d.rendering_button"
    bl_label = "図形表示/非表示切り替えボタン"
    bl_description = "図形の表示/非表示を切り替えるボタン"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        sc = context.scene
        if sc.rf_running is True:
            RenderFigure.handle_remove(self, context)
            sc.rf_running = False
        elif sc.rf_running is False:
            RenderFigure.handle_add(self, context)
            sc.rf_running = True

        return {'FINISHED'}
```

描画中にボタンが押された（ ```sc.rf_running``` が ```True``` ）時には、静的メソッド ```RenderFigure.handle_remove()``` を実行して描画関数を登録解除し、描画を中断します。
描画中でない場合にボタンが押された（ ```sc.rf_running``` が ```False``` ）時には、静的メソッド ```RenderFigure.handle_add()``` を実行して描画関数を登録し、描画を開始します。

## まとめ

PythonからOpenGLへアクセスするためのAPIである ```bgl``` モジュールを用いて、 *3Dビュー* エリアで図形を描画する方法を紹介しました。
今回紹介した ```bgl``` モジュールと [3.1節](01_Sample_7_Delete_face_by_mouse_click.md) で紹介したマウスからのイベントを扱う方法を組み合わせることで、Blender専用のUIとは全く異なる独自のUIを構築することができます。

ただし、OpenGLの全ての機能に対してAPIが用意されているわけではありません。
このため ```bgl``` モジュールを利用する際には、 [4.1節](../chapter_04/01_Research_official_Blender_API_for_Add-on.md) を参考にして、Blenderが提供するAPIを確認する必要があります。

<div id="point"></div>

### ポイント

<div id="point_item"></div>

* OpenGLへアクセスするためのAPIを利用するためには、 ```bgl``` モジュールをインポートする必要がある
* ```bgl``` モジュールを用いて、アドオン内でOpenGLを用いて描画するためには、 ```bpy.types.SpaceXXX.draw_handler_add()``` （XXX：描画するエリア）関数を用いて、描画用の静的メソッドまたは関数を登録する必要がある
* 登録した描画用の静的メソッドまたは関数は、アドオン無効化時に ```bpy.types.SpaceXXX.draw_handler_remove()``` 関数を用いて、登録解除する必要がある
* ```bgl``` モジュールはオリジナルのOpenGLの使い方と似たような方法で、OpenGLへのアクセス手段を提供する
* ```context.scene``` に登録したプロパティは、 パネル用クラスの ```draw()``` メソッドで ```self.layout.prop()``` 関数を用いることによりUIパーツとして登録できる
* ```bgl``` モジュールはOpenGLの関数をすべてサポートしていないため、事前に使いたいAPIが用意されているか確認が必要である