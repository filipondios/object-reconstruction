package com.app;

import java.io.IOException;
import com.reconstruction.Model;

public class Main {
    public static void main(String args[]) throws IOException {
        final String model_name = "cube";

        System.out.println("Loading model: " + model_name);
        Model.loadModel(model_name);
    }
}