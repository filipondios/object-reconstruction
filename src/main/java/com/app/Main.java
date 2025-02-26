package com.app;

import java.io.IOException;
import com.raylib.Colors;
import com.raylib.Raylib;
import com.raylib.Raylib.Camera3D;
import com.raylib.Raylib.Vector3;
import com.reconstruction.Model;
import com.reconstruction.View;
import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;


public class Main {

    @SuppressWarnings("resource")
    public static void main(String args[]) throws IOException {
        // Try to load the 3D Model
        final String model_name = "stairs";

        Model model = Model.loadModel(model_name);
        model.initialReconstruction();
        model.refineModel();
        System.out.println(model);

        
        // Proceed with the data visualization
        Raylib.SetTraceLogLevel(Raylib.LOG_ERROR);
        Raylib.InitWindow(1000, 1000, model_name);
        Raylib.SetTargetFPS(60);

        Camera3D camera = new Camera3D()
            ._position(new Vector3().x(40).y(40).z(40))
            .target(Raylib.Vector3Zero())
            .projection(Raylib.CAMERA_ORTHOGRAPHIC)
            .up(new Vector3().y(1))
            .fovy(90);

        while (!Raylib.WindowShouldClose()) {
            
            if (Raylib.IsKeyDown(Raylib.KEY_RIGHT)) {
                // Rotate the camera around the 'Y' axis counter-clockwise.
                camera._position(Raylib.Vector3RotateByAxisAngle(camera._position(),
                    new Vector3().y(1), 0.05f));
            
            } else if (Raylib.IsKeyDown(Raylib.KEY_LEFT)) {
                // Rotate the camera around the 'Y' axis clockwise.
                camera._position(Raylib.Vector3RotateByAxisAngle(camera._position(),
                    new Vector3().y(1), -0.05f));
            }

            Raylib.BeginDrawing();
            Raylib.ClearBackground(Colors.WHITE);
            Raylib.BeginMode3D(camera);

            // Draw space X,Y,Z axes in the range [0, 200]
            Raylib.DrawLine3D(Raylib.Vector3Zero(), new Vector3().x(200), Colors.BLACK);
            Raylib.DrawLine3D(Raylib.Vector3Zero(), new Vector3().y(200), Colors.BLACK);
            Raylib.DrawLine3D(Raylib.Vector3Zero(), new Vector3().z(200), Colors.BLACK);

            // Draw each detected vertex in each view
            for (View view : model.getViews()) {
                for (Vector3D vec : view.getVertices()) {
                    Vector3 raylib_translate = new Vector3()
                        .x((float) vec.getX())
                        .y((float) vec.getZ())
                        .z((float) vec.getY());
                    Raylib.DrawSphere(raylib_translate, 0.5f, Colors.BLUE);
                }
            }

            // Draw the reconstructed model vertices
            for (Vector3D vec : model.getVertices()) {
                Vector3 raylib_translate = new Vector3()
                    .x((float) vec.getX())
                    .y((float) vec.getZ())
                    .z((float) vec.getY());
                Raylib.DrawSphere(raylib_translate, 0.5f, Colors.BLACK);
            }

            Raylib.EndMode3D();
            Raylib.EndDrawing();
        }

        Raylib.CloseWindow();
    }
}