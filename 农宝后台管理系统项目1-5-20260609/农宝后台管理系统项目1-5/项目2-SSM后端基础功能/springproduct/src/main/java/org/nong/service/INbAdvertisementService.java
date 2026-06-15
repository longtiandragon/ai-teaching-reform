package org.nong.service;

import org.nong.common.Result;
import org.nong.entity.NbAdvertisement;
import java.util.Map;

public interface INbAdvertisementService {
    Result<NbAdvertisement> selectList(Map<String, Object> params);
    NbAdvertisement selectById(String id);
    int insert(NbAdvertisement ad);
    int update(NbAdvertisement ad);
    int deleteById(String id);
    int deleteBatch(String[] ids);
}

