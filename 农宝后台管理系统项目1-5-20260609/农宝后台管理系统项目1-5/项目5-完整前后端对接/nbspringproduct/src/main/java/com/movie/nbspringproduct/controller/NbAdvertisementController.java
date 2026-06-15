package com.movie.nbspringproduct.controller;

import com.movie.nbspringproduct.common.Result;
import com.movie.nbspringproduct.entity.NbAdvertisement;
import com.movie.nbspringproduct.service.INbAdvertisementService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 广告Controller
 */
@RestController
@RequestMapping("/dev-api/yjnb/advertisement")
public class NbAdvertisementController {
    
    @Autowired
    private INbAdvertisementService advertisementService;
    
    /**
     * 查询广告列表
     */
    @GetMapping("/list")
    public Result<List<NbAdvertisement>> list(NbAdvertisement advertisement) {
        List<NbAdvertisement> list = advertisementService.selectAdvertisementList(advertisement);
        return Result.success(list, (long) list.size());
    }
    
    /**
     * 获取广告详细信息
     */
    @GetMapping("/{id}")
    public Result<NbAdvertisement> getInfo(@PathVariable("id") String id) {
        return Result.success(advertisementService.selectAdvertisementById(id));
    }
    
    /**
     * 新增广告
     */
    @PostMapping
    public Result<Void> add(@RequestBody NbAdvertisement advertisement) {
        return advertisementService.insertAdvertisement(advertisement) > 0 ? 
                Result.success("新增成功") : Result.error("新增失败");
    }
    
    /**
     * 修改广告
     */
    @PutMapping
    public Result<Void> edit(@RequestBody NbAdvertisement advertisement) {
        return advertisementService.updateAdvertisement(advertisement) > 0 ? 
                Result.success("修改成功") : Result.error("修改失败");
    }
    
    /**
     * 删除广告
     */
    @DeleteMapping("/{ids}")
    public Result<Void> remove(@PathVariable String[] ids) {
        return advertisementService.deleteAdvertisementByIds(ids) > 0 ? 
                Result.success("删除成功") : Result.error("删除失败");
    }
    
    /**
     * 发布广告
     */
    @PostMapping("/publish")
    public Result<Void> publish(@RequestBody String[] ids) {
        return advertisementService.publishAdvertisement(ids) > 0 ? 
                Result.success("发布成功") : Result.error("发布失败");
    }
    
    /**
     * 取消发布广告
     */
    @PostMapping("/unpublish")
    public Result<Void> unpublish(@RequestBody String[] ids) {
        return advertisementService.unpublishAdvertisement(ids) > 0 ? 
                Result.success("取消发布成功") : Result.error("取消发布失败");
    }
}

