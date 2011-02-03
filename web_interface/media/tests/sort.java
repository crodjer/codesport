import java.lang.*;
import java.util.*;

class sort
{

    static Scanner scan=new Scanner(System.in);   //to take user input.

    //Randomly generating an array between 1 and 100.
    public static void genarr(int[] arr)
    {
        int i;
	double x;
	for(i=0;i<arr.length;i++)
	{
	    x=Math.random();
	    x=100*x+1;
	    arr[i]=(int)x;
	}
    }


    //function to find the prime numbers by checking for divisors upto the square root of the number.
    public static void findprime(int[] arr)
    {
	int i,j,flag=0,n;
	System.out.println("\n\nThe prime numbers are:");
	for(i=0;i<arr.length;i++)
	{
	    flag=0;
	    n=(int)Math.sqrt(arr[i]);
	    if(arr[i]<=1)
	        flag=1;
	    for(j=2;j<=n;j++)
            {
		if((arr[i]%j)==0)
		{
		    flag=1;
		    break;
		}

	    }
	    if(flag==0)
	        System.out.print(arr[i]+" ");
	}
	System.out.println("\n\n");
    }
    
    
    //function to merge the given array between the indices beg and end, whose 2 halves are already sorted
    public static void merge(int[] arr,int beg,int end)
    {
	int n,mid,i,j,k;
	n=end+1-beg;
	mid=beg+n/2;
	int[] temp=new int[n];
	i=beg;j=mid;k=0;
	while((i<mid)&&(j<=end))
	{
	    if(arr[i]<arr[j])
		temp[k++]=arr[i++];
	    else
		temp[k++]=arr[j++];
	}
	while(i<mid)
	    temp[k++]=arr[i++];
	while(j<=end)
	    temp[k++]=arr[j++];
	for(i=0;i<n;i++)
	{
	    arr[beg+i]=temp[i];
	}
    }

    
    //recrsive function to sort an array between the indices beg and end using merge sort algorithm. 
    public static void mergesort(int[] arr,int beg,int end)
    {
 	int mid;
	if(end==beg)
	    return;
	else
	{
	    mid=beg+((end+1-beg)/2);
	    mergesort(arr,beg,mid-1);
	    mergesort(arr,mid,end);
	    merge(arr,beg,end);
	}
    }
  
    public static void main(String[] args)
    {
        int i,no;
	int[] arr;
        no=scan.nextInt();
        arr=new int[no];
        for(i=0;i<no;i++)
           arr[i]=scan.nextInt();
	mergesort(arr,0,arr.length-1);
	for(i=0;i<arr.length;i++)
	{
	    System.out.print(arr[i]+"\t");
	}
	System.out.println("\n\n");

    }
}
