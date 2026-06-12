package org.nong.service.impl;

import org.nong.common.Result;
import org.nong.entity.NbAllowancePolicy;
import org.nong.mapper.NbAllowancePolicyMapper;
import org.nong.service.INbAllowancePolicyService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
public class NbAllowancePolicyServiceImpl implements INbAllowancePolicyService {
    
    @Autowired
    private NbAllowancePolicyMapper policyMapper;
    
    @Override
    @SuppressWarnings("unchecked")
    public Result<NbAllowancePolicy> selectList(Map<String, Object> params) {
        List<NbAllowancePolicy> list = policyMapper.selectList(params);
        Long total = policyMapper.selectCount(params);
        Result result = Result.success();
        result.setRows(list);
        result.setTotal(total);
        result.buildPageData();
        return result;
    }
    
    @Override
    public NbAllowancePolicy selectById(String id) {
        return policyMapper.selectById(id);
    }
    
    @Override
    public int insert(NbAllowancePolicy policy) {
        if (policy.getId() == null || policy.getId().isEmpty()) {
            policy.setId(UUID.randomUUID().toString().replace("-", ""));
        }
        return policyMapper.insert(policy);
    }
    
    @Override
    public int update(NbAllowancePolicy policy) {
        return policyMapper.update(policy);
    }
    
    @Override
    public int deleteById(String id) {
        return policyMapper.deleteById(id);
    }
    
    @Override
    public int deleteBatch(String[] ids) {
        return policyMapper.deleteBatch(ids);
    }
}

