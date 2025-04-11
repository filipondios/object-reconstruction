package com.app;

import com.core.Model;

public class Main {

    public static void main(String args[]) throws Exception {
        Model model = new Model("../models/cube");
        System.out.println(model);
        model.initialReconstruction();
    }
}