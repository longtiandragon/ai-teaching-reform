package com.movie.nbspringproduct.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.movie.nbspringproduct.entity.NbAllowancePolicy;
import com.movie.nbspringproduct.mapper.NbAllowancePolicyMapper;
import com.movie.nbspringproduct.service.INbAllowancePolicyService;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.Date;
import java.util.List;

/**
 * 补贴政策Service实现类
 */
@Service
public class NbAllowancePolicyServiceImpl extends ServiceImpl<NbAllowancePolicyMapper, NbAllowancePolicy> 
        implements INbAllowancePolicyService {
    
    @Override
    public List<NbAllowancePolicy> selectAllowancePolicyList(NbAllowancePolicy policy) {
        LambdaQueryWrapper<NbAllowancePolicy> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(StringUtils.isNotBlank(policy.getTitle()), NbAllowancePolicy::getTitle, policy.getTitle());
        wrapper.eq(StringUtils.isNotBlank(policy.getAuthor()), NbAllowancePolicy::getAuthor, policy.getAuthor());
        wrapper.eq(policy.getPublishStatus() != null, NbAllowancePolicy::getPublishStatus, policy.getPublishStatus());
        wrapper.eq(policy.getRecommend() != null, NbAllowancePolicy::getRecommend, policy.getRecommend());
        wrapper.orderByDesc(NbAllowancePolicy::getCreateTime);
        return this.list(wrapper);
    }
    
    @Override
    public NbAllowancePolicy selectAllowancePolicyById(String id) {
        return this.getById(id);
    }
    
    @Override
    public int insertAllowancePolicy(NbAllowancePolicy policy) {
        if (policy.getBrowseNum() == null) {
            policy.setBrowseNum(0);
        }
        if (policy.getPublishStatus() == null) {
            policy.setPublishStatus(0);
        }
        if (policy.getRecommend() == null) {
            policy.setRecommend(0);
        }
        return this.save(policy) ? 1 : 0;
    }
    
    @Override
    public int updateAllowancePolicy(NbAllowancePolicy policy) {
        return this.updateById(policy) ? 1 : 0;
    }
    
    @Override
    public int deleteAllowancePolicyByIds(String[] ids) {
        return this.removeByIds(Arrays.asList(ids)) ? 1 : 0;
    }
    
    @Override
    public int recommendAllowancePolicy(String[] ids) {
        List<NbAllowancePolicy> list = this.listByIds(Arrays.asList(ids));
        for (NbAllowancePolicy policy : list) {
            policy.setRecommend(1);
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
    
    @Override
    public int unrecommendAllowancePolicy(String[] ids) {
        List<NbAllowancePolicy> list = this.listByIds(Arrays.asList(ids));
        for (NbAllowancePolicy policy : list) {
            policy.setRecommend(0);
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
    
    @Override
    public int releaseAllowancePolicy(String[] ids) {
        List<NbAllowancePolicy> list = this.listByIds(Arrays.asList(ids));
        for (NbAllowancePolicy policy : list) {
            policy.setPublishStatus(1);
            policy.setPublishTime(new Date());
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
    
    @Override
    public int unreleaseAllowancePolicy(String[] ids) {
        List<NbAllowancePolicy> list = this.listByIds(Arrays.asList(ids));
        for (NbAllowancePolicy policy : list) {
            policy.setPublishStatus(0);
            policy.setPublishTime(null);
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
}

