package com.app;

import com.core.Model;
import com.util.ModelRender;

public class Main {

    public static void main(String args[]) throws Exception {
        final Model model = new Model("../models/short_cross");
        model.initialReconstruction(1);
        model.refineModel();
        
        final ModelRender render = new ModelRender(model);
        render.initialize();
        render.renderLoop();
    }
}