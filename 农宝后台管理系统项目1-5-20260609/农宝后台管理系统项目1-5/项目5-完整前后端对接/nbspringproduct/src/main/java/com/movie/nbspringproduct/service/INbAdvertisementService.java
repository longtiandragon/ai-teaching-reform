package com.movie.nbspringproduct.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.movie.nbspringproduct.entity.NbAdvertisement;

import java.util.List;

/**
 * 广告Service接口
 */
public interface INbAdvertisementService extends IService<NbAdvertisement> {
    
    /**
     * 查询广告列表
     */
    List<NbAdvertisement> selectAdvertisementList(NbAdvertisement advertisement);
    
    /**
     * 根据ID查询广告
     */
    NbAdvertisement selectAdvertisementById(String id);
    
    /**
     * 新增广告
     */
    int insertAdvertisement(NbAdvertisement advertisement);
    
    /**
     * 修改广告
     */
    int updateAdvertisement(NbAdvertisement advertisement);
    
    /**
     * 批量删除广告
     */
    int deleteAdvertisementByIds(String[] ids);
    
    /**
     * 发布广告
     */
    int publishAdvertisement(String[] ids);
    
    /**
     * 取消发布广告
     */
    int unpublishAdvertisement(String[] ids);
}

