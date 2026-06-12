package com.movie.nbspringproduct.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.movie.nbspringproduct.entity.NbAllowancePolicy;

import java.util.List;

/**
 * 补贴政策Service接口
 */
public interface INbAllowancePolicyService extends IService<NbAllowancePolicy> {
    
    /**
     * 查询补贴政策列表
     */
    List<NbAllowancePolicy> selectAllowancePolicyList(NbAllowancePolicy policy);
    
    /**
     * 查询补贴政策详细
     */
    NbAllowancePolicy selectAllowancePolicyById(String id);
    
    /**
     * 新增补贴政策
     */
    int insertAllowancePolicy(NbAllowancePolicy policy);
    
    /**
     * 修改补贴政策
     */
    int updateAllowancePolicy(NbAllowancePolicy policy);
    
    /**
     * 批量删除补贴政策
     */
    int deleteAllowancePolicyByIds(String[] ids);
    
    /**
     * 推荐补贴政策
     */
    int recommendAllowancePolicy(String[] ids);
    
    /**
     * 取消推荐补贴政策
     */
    int unrecommendAllowancePolicy(String[] ids);
    
    /**
     * 发布补贴政策
     */
    int releaseAllowancePolicy(String[] ids);
    
    /**
     * 取消发布补贴政策
     */
    int unreleaseAllowancePolicy(String[] ids);
}

