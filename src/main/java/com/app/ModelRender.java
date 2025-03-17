package com.app;

import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;
import org.apache.commons.math3.util.Pair;
import com.raylib.Colors;
import com.raylib.Raylib;
import com.raylib.Raylib.Camera3D;
import com.raylib.Raylib.Vector3;
import com.reconstruction.Model;
import com.reconstruction.View;

@SuppressWarnings("resource")
public class ModelRender {
 
    private float camera_speed;
    private Model model;
    private Camera3D camera;
    
    public ModelRender(Model model) {
        this.model = model;
        this.camera = new Camera3D()
            ._position(new Vector3().x(400).y(400).z(400))
            .target(Raylib.Vector3Zero())
            .projection(Raylib.CAMERA_ORTHOGRAPHIC)
            .up(new Vector3().y(1))
            .fovy(90);
        this.camera_speed = 0.05f;
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
        // Draw each detected vertex in each view
        for (View view : this.model.getViews()) {
            for (Vector3D vec : view.getVertices()) {
                Vector3 raylib_translate = new Vector3()
                    .x((float) vec.getX())
                    .y((float) vec.getZ())
                    .z((float) vec.getY());
                Raylib.DrawSphere(raylib_translate, 0.5f, Colors.BLUE);
            }
        }

        // Draw the reconstructed model vertices
        for (Vector3D vec : this.model.getVertices()) {
            Vector3 raylib_translate = new Vector3()
                .x((float) vec.getX())
                .y((float) vec.getZ())
                .z((float) vec.getY());
            Raylib.DrawSphere(raylib_translate, 0.5f, Colors.BLACK);
        }

        // Draw the reconstructed model edges.
        for (Pair<Vector3D, Vector3D> edge : this.model.getEdges()) {
            Vector3D a = edge.getKey();
            Vector3D b = edge.getValue();

            Vector3 raylib_translate_a = new Vector3()
                .x((float) a.getX())
                .y((float) a.getZ())
                .z((float) a.getY());

            Vector3 raylib_translate_b = new Vector3()
                .x((float) b.getX())
                .y((float) b.getZ())
                .z((float) b.getY());

            Raylib.DrawLine3D(raylib_translate_a, raylib_translate_b, Colors.BLACK);
        }
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