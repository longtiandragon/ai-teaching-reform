package com.movie.nbspringproduct.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.movie.nbspringproduct.entity.SysConfig;
import com.movie.nbspringproduct.mapper.SysConfigMapper;
import com.movie.nbspringproduct.service.ISysConfigService;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 系统配置Service实现类
 */
@Service
public class SysConfigServiceImpl extends ServiceImpl<SysConfigMapper, SysConfig> implements ISysConfigService {
    
    @Override
    public String getConfigValueByKey(String configKey) {
        LambdaQueryWrapper<SysConfig> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(SysConfig::getConfigKey, configKey);
        SysConfig config = getOne(wrapper);
        return config != null ? config.getConfigValue() : null;
    }
    
    @Override
    public Map<String, String> getAllConfigMap() {
        List<SysConfig> configList = list();
        Map<String, String> configMap = new HashMap<>();
        for (SysConfig config : configList) {
            configMap.put(config.getConfigKey(), config.getConfigValue());
        }
        return configMap;
    }
    
    @Override
    public void saveConfigBatch(Map<String, String> configMap) {
        for (Map.Entry<String, String> entry : configMap.entrySet()) {
            String key = entry.getKey();
            String value = entry.getValue();
            
            LambdaQueryWrapper<SysConfig> wrapper = new LambdaQueryWrapper<>();
            wrapper.eq(SysConfig::getConfigKey, key);
            SysConfig config = getOne(wrapper);
            
            if (config != null) {
                // 更新
                config.setConfigValue(value);
                updateById(config);
            } else {
                // 新增
                config = new SysConfig();
                config.setConfigKey(key);
                config.setConfigValue(value);
                config.setConfigName(key);
                config.setConfigType("N");
                save(config);
            }
        }
    }
}

