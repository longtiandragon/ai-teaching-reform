package org.nong.service.impl;

import org.nong.entity.SysConfig;
import org.nong.mapper.SysConfigMapper;
import org.nong.service.ISysConfigService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.UUID;

@Service
public class SysConfigServiceImpl implements ISysConfigService {
    
    @Autowired
    private SysConfigMapper configMapper;
    
    @Override
    public List<SysConfig> selectAll() {
        return configMapper.selectAll();
    }
    
    @Override
    public SysConfig selectById(String id) {
        return configMapper.selectById(id);
    }
    
    @Override
    public SysConfig selectByKey(String configKey) {
        return configMapper.selectByKey(configKey);
    }
    
    @Override
    public int insert(SysConfig config) {
        if (config.getId() == null || config.getId().isEmpty()) {
            config.setId(UUID.randomUUID().toString().replace("-", ""));
        }
        return configMapper.insert(config);
    }
    
    @Override
    public int update(SysConfig config) {
        return configMapper.update(config);
    }
    
    @Override
    public int updateByKey(SysConfig config) {
        return configMapper.updateByKey(config);
    }
    
    @Override
    public int batchUpdate(List<SysConfig> configs) {
        int count = 0;
        for (SysConfig config : configs) {
            if (config.getConfigKey() != null) {
                count += configMapper.updateByKey(config);
            }
        }
        return count;
    }
}

