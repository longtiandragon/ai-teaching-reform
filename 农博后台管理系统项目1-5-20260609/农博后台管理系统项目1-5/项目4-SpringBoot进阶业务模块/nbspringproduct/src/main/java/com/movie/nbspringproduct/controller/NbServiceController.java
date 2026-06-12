package com.movie.nbspringproduct.controller;

import com.movie.nbspringproduct.common.Result;
import com.movie.nbspringproduct.entity.NbService;
import com.movie.nbspringproduct.service.INbServiceService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 服务Controller
 */
@RestController
@RequestMapping("/dev-api/yjnb/service")
public class NbServiceController {
    
    @Autowired
    private INbServiceService serviceService;
    
    /**
     * 查询服务列表
     */
    @GetMapping("/list")
    public Result<List<NbService>> list(NbService service) {
        List<NbService> list = serviceService.selectServiceList(service);
        return Result.success(list, (long) list.size());
    }
    
    /**
     * 获取服务详细信息
     */
    @GetMapping("/{id}")
    public Result<NbService> getInfo(@PathVariable("id") String id) {
        return Result.success(serviceService.selectServiceById(id));
    }
    
    /**
     * 新增服务
     */
    @PostMapping
    public Result<Void> add(@RequestBody NbService service) {
        return serviceService.insertService(service) > 0 ? 
                Result.success("新增成功") : Result.error("新增失败");
    }
    
    /**
     * 修改服务
     */
    @PutMapping
    public Result<Void> edit(@RequestBody NbService service) {
        return serviceService.updateService(service) > 0 ? 
                Result.success("修改成功") : Result.error("修改失败");
    }
    
    /**
     * 删除服务
     */
    @DeleteMapping("/{ids}")
    public Result<Void> remove(@PathVariable String[] ids) {
        return serviceService.deleteServiceByIds(ids) > 0 ? 
                Result.success("删除成功") : Result.error("删除失败");
    }
}

