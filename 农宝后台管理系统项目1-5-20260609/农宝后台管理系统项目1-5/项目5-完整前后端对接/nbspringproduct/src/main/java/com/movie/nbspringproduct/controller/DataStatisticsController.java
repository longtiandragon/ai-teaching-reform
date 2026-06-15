package com.movie.nbspringproduct.controller;

import com.movie.nbspringproduct.common.Result;
import com.movie.nbspringproduct.service.INbAllowancePolicyService;
import com.movie.nbspringproduct.service.INbCreditLoanService;
import com.movie.nbspringproduct.service.INbFarmProduceService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.*;

/**
 * 数据统计Controller - 用于数据可视化大屏
 */
@RestController
@RequestMapping("/dev-api/statistics")
public class DataStatisticsController {

    @Autowired
    private INbAllowancePolicyService policyService;

    @Autowired
    private INbCreditLoanService loanService;

    @Autowired
    private INbFarmProduceService produceService;

    /**
     * 获取产品销量和浏览数统计
     */
    @GetMapping("/productStats")
    public Result<Map<String, Object>> getProductStats() {
        Map<String, Object> data = new HashMap<>();
        
        // 模拟产品销量数据（实际应从订单表统计）
        List<Map<String, Object>> salesData = new ArrayList<>();
        salesData.add(createCategoryData("有机大米", 320, 450));
        salesData.add(createCategoryData("新鲜蔬菜", 280, 380));
        salesData.add(createCategoryData("散养土鸡蛋", 360, 500));
        salesData.add(createCategoryData("红富士苹果", 240, 320));
        salesData.add(createCategoryData("明前龙井茶", 180, 220));
        salesData.add(createCategoryData("其他", 150, 200));
        
        data.put("salesData", salesData);
        return Result.success(data);
    }

    /**
     * 获取数据分布统计（饼图）
     */
    @GetMapping("/distribution")
    public Result<Map<String, Object>> getDistribution() {
        Map<String, Object> data = new HashMap<>();
        
        // 按类别统计农产品数量
        List<Map<String, Object>> categoryData = new ArrayList<>();
        categoryData.add(createPieData("粮食", 35, "#5470c6"));
        categoryData.add(createPieData("蔬菜", 28, "#91cc75"));
        categoryData.add(createPieData("水果", 22, "#fac858"));
        categoryData.add(createPieData("禽蛋", 18, "#ee6666"));
        categoryData.add(createPieData("茶叶", 15, "#73c0de"));
        categoryData.add(createPieData("其他", 12, "#3ba272"));
        
        data.put("categoryData", categoryData);
        return Result.success(data);
    }

    /**
     * 获取月度趋势数据（折线图）
     */
    @GetMapping("/monthlyTrend")
    public Result<Map<String, Object>> getMonthlyTrend() {
        Map<String, Object> data = new HashMap<>();
        
        // 月度数据（最近6个月）
        List<String> months = Arrays.asList("2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12");
        List<Integer> sales = Arrays.asList(450, 380, 320, 280, 240, 210);
        List<Integer> browse = Arrays.asList(580, 520, 460, 410, 370, 340);
        
        data.put("months", months);
        data.put("sales", sales);
        data.put("browse", browse);
        
        return Result.success(data);
    }

    /**
     * 获取综合统计概览
     */
    @GetMapping("/overview")
    public Result<Map<String, Object>> getOverview() {
        Map<String, Object> data = new HashMap<>();
        
        // 统计各类数据总数
        long policyCount = policyService.count();
        long loanCount = loanService.count();
        long produceCount = produceService.count();
        
        // 计算总浏览量（从数据库实际统计）
        Integer totalBrowse = produceService.list().stream()
                .mapToInt(p -> p.getBrowseNum() != null ? p.getBrowseNum() : 0)
                .sum();
        
        data.put("policyCount", policyCount);
        data.put("loanCount", loanCount);
        data.put("produceCount", produceCount);
        data.put("totalBrowse", totalBrowse);
        data.put("totalSales", 1520); // 模拟总销量
        data.put("monthlyIncrease", -12.5); // 月度增长率（%）
        
        return Result.success(data);
    }

    // 辅助方法：创建类别数据
    private Map<String, Object> createCategoryData(String name, int sales, int browse) {
        Map<String, Object> item = new HashMap<>();
        item.put("name", name);
        item.put("sales", sales);
        item.put("browse", browse);
        return item;
    }

    // 辅助方法：创建饼图数据
    private Map<String, Object> createPieData(String name, int value, String color) {
        Map<String, Object> item = new HashMap<>();
        item.put("name", name);
        item.put("value", value);
        item.put("itemStyle", Collections.singletonMap("color", color));
        return item;
    }
}

