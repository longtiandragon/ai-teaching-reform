package org.nong.service;

import org.nong.common.Result;
import org.nong.entity.NbAllowancePolicy;

import java.util.Map;

public interface INbAllowancePolicyService {
    Result<NbAllowancePolicy> selectList(Map<String, Object> params);
    NbAllowancePolicy selectById(String id);
    int insert(NbAllowancePolicy policy);
    int update(NbAllowancePolicy policy);
    int deleteById(String id);
    int deleteBatch(String[] ids);
}

