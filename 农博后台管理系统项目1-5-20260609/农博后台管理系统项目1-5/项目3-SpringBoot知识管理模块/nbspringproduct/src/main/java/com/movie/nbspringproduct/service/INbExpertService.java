package com.movie.nbspringproduct.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.movie.nbspringproduct.entity.NbExpert;

import java.util.List;

/**
 * 专家Service接口
 */
public interface INbExpertService extends IService<NbExpert> {
    
    /**
     * 查询专家列表
     */
    List<NbExpert> selectExpertList(NbExpert expert);
    
    /**
     * 根据ID查询专家
     */
    NbExpert selectExpertById(String id);
    
    /**
     * 新增专家
     */
    int insertExpert(NbExpert expert);
    
    /**
     * 修改专家
     */
    int updateExpert(NbExpert expert);
    
    /**
     * 批量删除专家
     */
    int deleteExpertByIds(String[] ids);
}

