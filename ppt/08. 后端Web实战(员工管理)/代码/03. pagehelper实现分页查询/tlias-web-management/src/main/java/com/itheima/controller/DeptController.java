package com.itheima.controller;

import com.itheima.pojo.Dept;
import com.itheima.pojo.Result;
import com.itheima.service.DeptService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 部门管理Controller
 */
@Slf4j
@RequestMapping("/depts")
@RestController
public class DeptController {

    //定义一个日志记录器
    //private static final Logger log = LoggerFactory.getLogger(DeptController.class);

    @Autowired
    private DeptService deptService;

    /**
     * 查询全部部门
     */
    //@RequestMapping(value = "/depts", method = RequestMethod.GET)
    @GetMapping
    public Result list(){
        log.info("查询全部部门 ~ ");
        List<Dept> deptList = deptService.list();
        return Result.success(deptList);
    }


    /**
     * 根据ID删除部门 --> /depts?id=10
     * 方式一 : HttpServletRequest 获取 (不推荐)
     */
    /*@DeleteMapping("/depts")
    public Result delete(HttpServletRequest request){
        //获取请求参数id
        String idStr = request.getParameter("id");
        Integer id = Integer.parseInt(idStr);
        System.out.println("根据ID删除部门 ~ " + id);
        return Result.success();
    }*/

    /**
     * 根据ID删除部门 --> /depts?id=10
     * 方式二 : @RequestParam 注解, 将前端传递的请求参数绑定给方法形参; 应用场景: 前端传递参数名 与 方法形参名 不一致 .
     */
    /*@DeleteMapping("/depts")
    public Result delete(@RequestParam(value = "id", required = false) Integer abc){
        System.out.println("根据ID删除部门 ~ " + abc);
        return Result.success();
    }*/

    /**
     * 根据ID删除部门 --> /depts?id=10
     * 方式三: 直接定义形参接收 ---> 保证前端请求参数名 与 方法形参名一致 --> (推荐)
     */
    @DeleteMapping
    public Result delete(Integer id){
        log.info("根据ID删除部门 ~ , {}", id);
        deptService.delete(id);
        return Result.success();
    }

    /**
     * 添加部门
     *  {“name”：“教研部”} -----------> @RequestBody 实体对象 Dept dept
     */
    @PostMapping
    public Result add(@RequestBody Dept dept){
        log.info("添加部门 : {}", dept);
        deptService.add(dept);
        return Result.success();
    }

    /**
     * 根据ID查询部门  ---> /depts/1
     *                    /depts/2
     *                    /depts/5
     */
    @GetMapping("/{id}")
    public Result getInfo(@PathVariable Integer id){
        log.info("根据ID查询部门 ~ : {}", id);
        Dept dept =  deptService.getInfo(id);
        return Result.success(dept);
    }

    /**
     * 修改部门  {"id":1, "name":"xxxxx"}
     */
    @PutMapping
    public Result update(@RequestBody Dept dept){
        log.info("修改部门 ~ : {}", dept);
        deptService.update(dept);
        return Result.success();
    }
}
