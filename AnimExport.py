import bpy
import json, traceback


# To Pose Position
# =================================================================================================
class ANIME_POSE_TOOLS_OT_anim_export(bpy.types.Operator):
    bl_idname = "anime_pose_tools.anim_export"
    bl_label = "Export Animations"

    # ファイル選択ダイアログ
    filepath: bpy.props.StringProperty()
    filter_glob: bpy.props.StringProperty(
        default="*.json",
    )
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    # execute
    def execute(self, context):
        armature = bpy.context.view_layer.objects.active
        if armature.type != "ARMATURE":
            self.report({'ERROR'}, "activeなオブジェクトがArmatureじゃない(通常あり得ない)")
            return {'CANCELLED'}

        # かならず.jsonに
        if not self.filepath.lower().endswith(".json"):
            self.filepath += ".json"

        data = {}
        data["bones"] = ["Bone", "Bone.001", "Bone.002", "Bone.003"]
        data["animation"] = self.get_animation_data(data["bones"])

        try:
            with open(self.filepath, 'w') as f:
                json.dump(data, f, indent=4)
        except:
            self.report({'ERROR'}, traceback.format_exc())
            return {'CANCELLED'}


        return {'FINISHED'}

    def get_animation_data(self, bones):
        actions = {}
        for action in bpy.data.actions:
            action_data = self.get_action_data(action, bones)

            # データがあったら登録
            if action_data:
                actions[action.name] = action_data

            # # ボーン名と適用対象の取得
            # match = re.search(r'pose.bones\["(.+?)"\].+?([^.]+$)', fcurve.data_path)
            # if match:
            #     bone_name, attribute = match.groups()

            # # ActiveBoneだけ処理
            # if bone_name == target_bone.name:
            #     # 回転だけコピー
            #     if attribute != "rotation_quaternion" and attribute != "rotation_euler" and attribute != "rotation_axis_angle":
            #         continue
            #     keyframes["%s:%d" % (attribute, fcurve.array_index)] = fcurve.keyframe_points

        return actions

    def get_action_data(self, action, bones):
        fcurves = {}
        for fcurve in action.fcurves:
            # bone名はリストで一括変更できるように、インデックス番号で扱う
            try:
                bone_index = bones.index(fcurve.group.name)
            except:
                continue

            if bone_index not in fcurves:
                fcurves[bone_index] = {}

            # fcurve設定
            attribute = fcurve.data_path.split(".")[-1]
            if attribute not in fcurves[bone_index]:
                fcurves[bone_index][attribute] = {}

            # point設定
            point_array = []
            for point in fcurve.keyframe_points:
                point_data = {
                    "co": point.co.to_tuple(),
                    "easing": point.easing,
                    "handle_left": point.handle_left.to_tuple(),
                    "handle_left_type": point.handle_left_type,
                    "handle_right": point.handle_right.to_tuple(),
                    "handle_right_type": point.handle_right_type,
                    "interpolation": point.interpolation,
                    "period": point.period,
                    "type": point.type,
                }
                point_array.append(point_data)
            fcurves[bone_index][attribute][fcurve.array_index] = point_array

        return fcurves



# To Rest Position
# =================================================================================================
class ANIME_POSE_TOOLS_OT_anim_import(bpy.types.Operator):
    bl_idname = "anime_pose_tools.anim_import"
    bl_label = "Import Animations"

    # ファイル選択ダイアログ
    filepath: bpy.props.StringProperty()
    filter_glob: bpy.props.StringProperty(
        default="*.json",
    )
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    # execute
    def execute(self, context):
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
        except:
            self.report({'ERROR'}, traceback.format_exc())
            return {'CANCELLED'}

        print(data)

        return {'FINISHED'}


# UI描画設定
# =================================================================================================
def ui_draw(context, layout):
    layout.label(text="Export/Import Animations:")
    box = layout.box()
    box.operator("anime_pose_tools.anim_export")
    box.operator("anime_pose_tools.anim_import")