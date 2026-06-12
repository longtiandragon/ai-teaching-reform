package com.movie.nbspringproduct.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.movie.nbspringproduct.entity.NbService;

import java.util.List;

/**
 * 服务Service接口
 */
public interface INbServiceService extends IService<NbService> {
    
    /**
     * 查询服务列表
     */
    List<NbService> selectServiceList(NbService service);
    
    /**
     * 根据ID查询服务
     */
    NbService selectServiceById(String id);
    
    /**
     * 新增服务
     */
    int insertService(NbService service);
    
    /**
     * 修改服务
     */
    int updateService(NbService service);
    
    /**
     * 批量删除服务
     */
    int deleteServiceByIds(String[] ids);
}

