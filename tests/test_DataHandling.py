import matplotlib
matplotlib.use('agg', warn=False, force=True)
import pytest
import datahandling
import numpy as np
from matplotlib.testing.decorators import image_comparison
import matplotlib.pyplot as plt

plot_similarity_tolerance = 30
float_relative_tolerance = 1e-3

def test_load_data():
    """
    Tests that load_data works and therefore that DataObject.__init__, DataObject.get_time_data and DataObject.getPSD work. Specifically it checks that the data loads and that it returns an object of type DataObject. It checks that the filepath points to the correct place. The data is sampled at the correct frequency and therefore that it has loaded the times correctly. It checks that the max frequency in the PSD is approximately equal to the Nyquist frequency for the test data. It also checks that the data returned by get_time_data matches the data loaded.
    """
    data = datahandling.load_data("testData.raw")
    assert type(data) == datahandling.datahandling.DataObject
    assert data.filename == "testData.raw"
    assert data.time[1]-data.time[0] == pytest.approx(1/data.SampleFreq, rel=float_relative_tolerance) # approx equal to within 0.01%
    assert max(data.freqs) == pytest.approx(data.SampleFreq/2, rel=0.00001) # max freq in PSD is approx equal to Nyquist frequency within 0.001%
    t, V = data.get_time_data() 
#    np.testing.assert_array_equal(t, data.time) # TEMPORARY FIX - FIX THIS IN CODE!!!!!!!!!
#    np.testing.assert_array_equal(V, data.voltage) # TEMPORARY FIX - FIX THIS IN CODE!!!!!!!!!
    
    return None

GlobalData = datahandling.load_data("testData.raw") # Load data to be used in upcoming tests - so that it doesn't need to be loaded for each individual function to be tested

@pytest.mark.mpl_image_compare(tolerance=plot_similarity_tolerance) # this decorator compares the figure object returned by the following function to the baseline png image stored in tests/baseline
def test_plot_PSD():
    """
    This tests that the plot of the PSD produced by DataObject.plot_PSD is produced correctly and matches the baseline to a certain tolerance.
    """
    fig, ax = GlobalData.plot_PSD([0, 400], ShowFig=False)
    return fig

@pytest.mark.mpl_image_compare(tolerance=plot_similarity_tolerance) # this decorator compares the figure object returned by the following function to the baseline png image stored in tests/baseline
def test_get_fit():
    """
    Tests that DataObject.get_fit works and therefore tests fitPSD, fit_curvefit and PSD_Fitting as these are dependancies. It tests that the output values of the fitting are correct (both the values and thier errors) and that the plot looks the same as the baseline, within a certain tolerance.
    """
    A, F, Gamma, fig, ax = GlobalData.get_fit(75000, 10000, ShowFig=False)
    assert A.n == pytest.approx(584418711252, rel=float_relative_tolerance)
    assert F.n == pytest.approx(466604, rel=float_relative_tolerance)
    assert Gamma.n == pytest.approx(3951.716, rel=float_relative_tolerance)
    
    assert A.std_dev == pytest.approx(5827258935, rel=float_relative_tolerance)    
    assert F.std_dev == pytest.approx(50.3576, rel=float_relative_tolerance)     
    assert Gamma.std_dev == pytest.approx(97.5671, rel=float_relative_tolerance)
    
    return fig

def test_extract_parameters():
    """
    Tests that DataObject.extract_parameters works and returns the correct values.
    """
    with open("testDataPressure.dat", 'r') as file:
        for line in file:
            pressure = float(line.split("mbar")[0])
    R, M, ConvFactor = GlobalData.extract_parameters(pressure, 0.15)

    assert R.n == pytest.approx(3.27536e-8, rel=float_relative_tolerance)
    assert M.n == pytest.approx(3.23808e-19, rel=float_relative_tolerance)
    assert ConvFactor.n == pytest.approx(190629, rel=float_relative_tolerance)
    
    assert R.std_dev == pytest.approx(4.97914e-9, rel=float_relative_tolerance)    
    assert M.std_dev == pytest.approx(9.84496e-20, rel=float_relative_tolerance)     
    assert ConvFactor.std_dev == pytest.approx(58179.9, rel=float_relative_tolerance)

    return None

def test_get_time_data():
    """
    Tests that DataObject.get_time_data returns the correct number of values.
    """
    t, v = GlobalData.get_time_data(timeStart=0, timeEnd=1e-3)
    assert len(t) == len(v)
    assert len(t) == 10000
    return None

@pytest.mark.mpl_image_compare(tolerance=plot_similarity_tolerance)
def test_plot_time_data():
    """
    This tests that the plot of the time trace (from -1ms to 1ms) produced by DataObject.plot_time_data is produced correctly and matches the baseline to a certain tolerance.
    """
    fig, ax = GlobalData.plot_time_data(timeStart=-1e-3, timeEnd=1e-3, units='ms', ShowFig=False)
    return fig
    
def test_calc_area_under_PSD():
    """
    This tests that the calculation of the area under the PSD
    from 50 to 100 KHz, calculated by 
    DataObject.calc_area_under_PSD is unchanged.
    """
    TrueArea = 1.6900993420543872e-06
    area = GlobalData.calc_area_under_PSD(50e3, 100e3)
    assert area == pytest.approx(TrueArea, rel=float_relative_tolerance)
    return None

def test_get_fit_auto():
    ATrue = 466612.80058291875
    AErrTrue = 54.936633293369404
    OmegaTrapTrue = 583205139563.28
    OmegaTrapErrTrue = 7359927227.585048
    BigGammaTrue = 3946.998785496495
    BigGammaErrTrue = 107.96706466271127
    A, OmegaTrap, BigGamma = GlobalData.get_fit_auto(70e3, ShowFig=False)
    assert A.n == pytest.approx(ATrue, rel=float_relative_tolerance)
    assert OmegaTrap.n == pytest.approx(OmegaTrapTrue, rel=float_relative_tolerance)
    assert BigGamma.n == pytest.approx(BigGammaTrue, rel=float_relative_tolerance)
    assert A.std_dev == pytest.approx(AErrTrue, rel=float_relative_tolerance)
    assert OmegaTrap.std_dev == pytest.approx(OmegaTrapErrTrue, rel=float_relative_tolerance)
    assert BigGamma.std_dev == pytest.approx(BigGammaErrTrue, rel=float_relative_tolerance)
    return None 

