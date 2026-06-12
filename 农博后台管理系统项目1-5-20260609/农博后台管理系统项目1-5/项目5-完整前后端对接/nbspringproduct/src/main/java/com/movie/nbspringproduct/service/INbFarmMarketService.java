package com.movie.nbspringproduct.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.movie.nbspringproduct.entity.NbFarmMarket;

import java.util.List;

/**
 * 农贸市场Service接口
 */
public interface INbFarmMarketService extends IService<NbFarmMarket> {
    
    /**
     * 查询农贸市场列表
     */
    List<NbFarmMarket> selectFarmMarketList(NbFarmMarket market);
    
    /**
     * 查询农贸市场详细
     */
    NbFarmMarket selectFarmMarketById(Integer id);
    
    /**
     * 新增农贸市场
     */
    int insertFarmMarket(NbFarmMarket market);
    
    /**
     * 修改农贸市场
     */
    int updateFarmMarket(NbFarmMarket market);
    
    /**
     * 批量删除农贸市场
     */
    int deleteFarmMarketByIds(Integer[] ids);
}

