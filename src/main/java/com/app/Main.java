package com.app;

import java.awt.Color;
import java.io.IOException;
import com.raylib.Colors;
import com.raylib.Raylib;
import com.raylib.Raylib.Camera3D;
import com.raylib.Raylib.Vector3;
import com.reconstruction.Model;
import com.reconstruction.View;


public class Main {

    @SuppressWarnings("resource")
    public static void main(String args[]) throws IOException {
        // Try to load the 3D Model
        final String model_name = "cross";

        Model model = Model.loadModel(model_name);
        System.out.println(model);

        // Proceed with the data visualization
        Raylib.SetTraceLogLevel(Raylib.LOG_ERROR);
        Raylib.InitWindow(1000, 1000, model_name);
        Raylib.SetTargetFPS(60);

        Camera3D camera = new Camera3D()
            ._position(new Vector3().x(40).y(40).z(40))
            .target(new Vector3())
            .projection(Raylib.CAMERA_ORTHOGRAPHIC)
            .up(new Vector3().y(1))
            .fovy(90);

        while (!Raylib.WindowShouldClose()) {
            Raylib.BeginDrawing();
            Raylib.ClearBackground(Colors.WHITE);
            Raylib.BeginMode3D(camera);

            // Draw space X,Y,Z axes in the range [0, 200]
            Raylib.DrawLine3D(new Vector3(), new Vector3().x(200), Colors.BLACK);
            Raylib.DrawLine3D(new Vector3(), new Vector3().y(200), Colors.BLACK);
            Raylib.DrawLine3D(new Vector3(), new Vector3().z(200), Colors.BLACK);

            // Draw each detected vertex in each view
            for (View view : model.getViews()) {
                for (Vector3 vertex : view.vertices) {
                    Raylib.DrawSphere(vertex, 0.5f, Colors.BLACK);
                }
            }

            // Draw the model reconstructed vertices.
            for (Vector3 vertex : model.getVertices()) {
                Raylib.DrawSphere(vertex, 1, Colors.BLACK);
            }

            Raylib.EndMode3D();
            Raylib.EndDrawing();
        }

        Raylib.CloseWindow();
    }
}