package org.nong.service;

import org.nong.common.Result;
import org.nong.entity.NbService;
import java.util.Map;

public interface INbServiceService {
    Result<NbService> selectList(Map<String, Object> params);
    NbService selectById(String id);
    int insert(NbService service);
    int update(NbService service);
    int deleteById(String id);
    int deleteBatch(String[] ids);
}

