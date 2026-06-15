package org.nong.service.impl;

import org.nong.common.Result;
import org.nong.entity.NbAdvertisement;
import org.nong.mapper.NbAdvertisementMapper;
import org.nong.service.INbAdvertisementService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
public class NbAdvertisementServiceImpl implements INbAdvertisementService {
    
    @Autowired
    private NbAdvertisementMapper adMapper;
    
    @Override
    @SuppressWarnings("unchecked")
    public Result<NbAdvertisement> selectList(Map<String, Object> params) {
        List<NbAdvertisement> list = adMapper.selectList(params);
        Long total = adMapper.selectCount(params);
        Result result = Result.success();
        result.setRows(list);
        result.setTotal(total);
        result.buildPageData();
        return result;
    }
    
    @Override
    public NbAdvertisement selectById(String id) {
        return adMapper.selectById(id);
    }
    
    @Override
    public int insert(NbAdvertisement ad) {
        if (ad.getId() == null || ad.getId().isEmpty()) {
            ad.setId(UUID.randomUUID().toString().replace("-", ""));
        }
        return adMapper.insert(ad);
    }
    
    @Override
    public int update(NbAdvertisement ad) {
        return adMapper.update(ad);
    }
    
    @Override
    public int deleteById(String id) {
        return adMapper.deleteById(id);
    }
    
    @Override
    public int deleteBatch(String[] ids) {
        return adMapper.deleteBatch(ids);
    }
}

