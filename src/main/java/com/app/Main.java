package com.app;

import java.io.IOException;
import com.core.Model;
import com.core.ModelRender;

public class Main {

    public static void main(String args[]) throws IOException {
        // Try to load the 3D Model
        Model model = new Model("cube");
        model.initialReconstruction();
        model.refineModel();
        model.generateEdges();
        System.out.println(model);

        // Render the obtained 3D model
        ModelRender render = new ModelRender(model);
        render.initialize();
        render.renderLoop();
    }
}