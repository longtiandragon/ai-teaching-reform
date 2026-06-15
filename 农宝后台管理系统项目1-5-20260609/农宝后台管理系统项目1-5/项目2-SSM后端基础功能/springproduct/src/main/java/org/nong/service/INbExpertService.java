package org.nong.service;

import org.nong.common.Result;
import org.nong.entity.NbExpert;
import java.util.Map;

public interface INbExpertService {
    Result<NbExpert> selectList(Map<String, Object> params);
    NbExpert selectById(String id);
    int insert(NbExpert expert);
    int update(NbExpert expert);
    int deleteById(String id);
    int deleteBatch(String[] ids);
}

