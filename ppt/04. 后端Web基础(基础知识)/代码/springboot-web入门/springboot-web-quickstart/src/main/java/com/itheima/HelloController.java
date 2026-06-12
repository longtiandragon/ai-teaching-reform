package com.itheima;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController //标识当前是一个请求处理类
public class HelloController {

    @RequestMapping("/hello")
    public String hello(String name){
        System.out.println("Hello Controller ... hello ： " + name);
        return "Hello " + name + "~";
    }

}
