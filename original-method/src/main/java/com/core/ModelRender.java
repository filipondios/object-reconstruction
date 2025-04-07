package com.core;

import com.raylib.Colors;
import com.raylib.Raylib;
import com.raylib.Raylib.Camera3D;
import com.raylib.Raylib.Vector3;

@SuppressWarnings("resource")
public class ModelRender {
 
    private float camera_speed;
    private Camera3D camera;
    private boolean draw_model_vertices;
    private boolean draw_view_vertices;

    public ModelRender(Model model) {
        this.camera = new Camera3D()
            ._position(new Vector3().x(400).y(400).z(400))
            .target(Raylib.Vector3Zero())
            .projection(Raylib.CAMERA_ORTHOGRAPHIC)
            .up(new Vector3().y(1))
            .fovy(90);
        this.camera_speed = 0.05f;
    }

    public void showModelVertices(boolean show) {
        this.draw_model_vertices = show;
    }

    public void showViewVertices(boolean show) {
        this.draw_view_vertices = show;
    }

    public void initialize() {
        Raylib.SetTraceLogLevel(Raylib.LOG_ERROR);
        Raylib.InitWindow(1000, 1000, "Model visualization");
        Raylib.SetTargetFPS(60);
    }

    public void renderLoop() {
        while (!Raylib.WindowShouldClose()) {
            this.handleInput();
            Raylib.BeginDrawing();
            Raylib.ClearBackground(Colors.WHITE);
            Raylib.BeginMode3D(camera);
            this.drawModel();
            Raylib.EndMode3D();
            Raylib.EndDrawing();
        }
        Raylib.CloseWindow();
    }

    private void drawModel() {
        // TODO
    }

    private void handleInput() {
        if (Raylib.IsKeyDown(Raylib.KEY_RIGHT)) {
            // Rotate the camera around the 'Y' axis counter-clockwise.
            this.camera._position(Raylib.Vector3RotateByAxisAngle(camera._position(),
                new Vector3().y(100), this.camera_speed));
        
        } else if (Raylib.IsKeyDown(Raylib.KEY_LEFT)) {
            // Rotate the camera around the 'Y' axis clockwise.
            camera._position(Raylib.Vector3RotateByAxisAngle(camera._position(),
                new Vector3().y(100), -this.camera_speed));
        }
    }
}