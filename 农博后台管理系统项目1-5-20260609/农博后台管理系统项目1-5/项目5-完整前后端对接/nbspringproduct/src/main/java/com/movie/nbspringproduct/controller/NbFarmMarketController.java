package com.movie.nbspringproduct.controller;

import com.movie.nbspringproduct.common.Result;
import com.movie.nbspringproduct.entity.NbFarmMarket;
import com.movie.nbspringproduct.service.INbFarmMarketService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 农贸市场Controller
 */
@RestController
@RequestMapping("/dev-api/yjnb/market")
public class NbFarmMarketController {
    
    @Autowired
    private INbFarmMarketService farmMarketService;
    
    /**
     * 查询农贸市场列表
     */
    @GetMapping("/list")
    public Result<List<NbFarmMarket>> list(NbFarmMarket market) {
        List<NbFarmMarket> list = farmMarketService.selectFarmMarketList(market);
        return Result.success(list, (long) list.size());
    }
    
    /**
     * 获取农贸市场详细信息
     */
    @GetMapping("/{id}")
    public Result<NbFarmMarket> getInfo(@PathVariable("id") Integer id) {
        return Result.success(farmMarketService.selectFarmMarketById(id));
    }
    
    /**
     * 新增农贸市场
     */
    @PostMapping
    public Result<Void> add(@RequestBody NbFarmMarket market) {
        return farmMarketService.insertFarmMarket(market) > 0 ? 
                Result.success("新增成功") : Result.error("新增失败");
    }
    
    /**
     * 修改农贸市场
     */
    @PutMapping
    public Result<Void> edit(@RequestBody NbFarmMarket market) {
        return farmMarketService.updateFarmMarket(market) > 0 ? 
                Result.success("修改成功") : Result.error("修改失败");
    }
    
    /**
     * 删除农贸市场
     */
    @DeleteMapping("/{ids}")
    public Result<Void> remove(@PathVariable Integer[] ids) {
        return farmMarketService.deleteFarmMarketByIds(ids) > 0 ? 
                Result.success("删除成功") : Result.error("删除失败");
    }
    
    /**
     * 导出农贸市场列表
     */
    @PostMapping("/export")
    public Result<List<NbFarmMarket>> export(NbFarmMarket market) {
        List<NbFarmMarket> list = farmMarketService.selectFarmMarketList(market);
        return Result.success(list);
    }
}

